using System;
using System.Collections.Generic;
using House4696.Core;
using House4696.Generation;
using House4696.Model;
using House4696.Runtime;
using House4696.Setup;
using UnityEngine;
using UnityEngine.Rendering;
using Object = UnityEngine.Object;

namespace House4696.App
{
    /// <summary>
    /// The open project: its document, the generated house in the scene and an undo history. Every change goes
    /// through <see cref="Apply"/>: validate → save → rebuild (a house regenerates in well under a second).
    /// </summary>
    public sealed class HouseSession
    {
        const int UndoDepth = 30;

        public readonly ProjectStore Store;
        public string ProjectId { get; private set; }
        public HouseDocument Doc { get; private set; }
        public HouseBuildResult Result { get; private set; }
        public List<Issue> Issues { get; private set; } = new List<Issue>();
        public long LastBuildMs { get; private set; }
        /// <summary>Set after a rebuild: the reflection probes should be re-captured once the GI has settled.</summary>
        public bool ProbesDirty { get; set; }
        public event Action Rebuilt;

        readonly MaterialLibrary _mats;
        readonly List<string> _undo = new List<string>();
        SceneWriter _writer;

        public HouseSession(ProjectStore store, MaterialLibrary mats)
        {
            Store = store; _mats = mats;
        }

        public bool HasProject => Doc != null;
        public int UndoCount => _undo.Count;

        public void Open(string id)
        {
            var doc = Store.Load(id);
            ProjectId = id;
            Doc = doc;
            _undo.Clear();
            Rebuild();
        }

        public void Close()
        {
            Teardown();
            ProjectId = null; Doc = null; Result = null; _undo.Clear();
        }

        /// <summary>Makes <paramref name="next"/> the current document (saved, rebuilt); the old one goes to the undo stack.</summary>
        public List<Issue> Apply(HouseDocument next)
        {
            if (!HasProject) throw new InvalidOperationException("нет открытого проекта — открой или создай проект");
            _undo.Add(HouseJson.Serialize(Doc));
            if (_undo.Count > UndoDepth) _undo.RemoveAt(0);
            Doc = next;
            Store.Save(ProjectId, Doc);
            Rebuild();
            return Issues;
        }

        public bool Undo()
        {
            if (_undo.Count == 0) return false;
            Doc = HouseJson.Deserialize(_undo[_undo.Count - 1]);
            _undo.RemoveAt(_undo.Count - 1);
            Store.Save(ProjectId, Doc);
            Rebuild();
            return true;
        }

        public void Rebuild()
        {
            var sw = System.Diagnostics.Stopwatch.StartNew();
            Teardown();
            Issues = HouseValidator.Validate(Doc);
            _writer = new SceneWriter();
            // generation works on a copy: the builder normalises some fields (level order) in place
            Result = HouseBuilder.Build(HouseJson.Clone(Doc), _mats, _writer);
            PrepareScene();
            LastBuildMs = sw.ElapsedMilliseconds;
            ProbesDirty = true;
            Rebuilt?.Invoke();
        }

        void PrepareScene()
        {
            int layer = LayerMask.NameToLayer("House");
            if (layer >= 0)
                foreach (var t in Result.House.GetComponentsInChildren<Transform>(true)) t.gameObject.layer = layer;
            foreach (var p in Result.House.GetComponentsInChildren<ReflectionProbe>(true))
            {
                p.mode = ReflectionProbeMode.Realtime;
                p.refreshMode = ReflectionProbeRefreshMode.ViaScripting;
                p.timeSlicingMode = ReflectionProbeTimeSlicingMode.NoTimeSlicing;
            }
            var site = Doc.Site ?? new SiteDef();
            if (RenderSettings.sun != null)
                RenderSettings.sun.transform.rotation = Quaternion.Euler(EnvironmentBuilder.SunFrom(site.SunAzimuth, site.SunElevation));

            var cam = Camera.main;
            var viewer = cam != null ? cam.GetComponent<HouseViewer>() : null;
            if (viewer != null)
            {
                var walk = Result.Walk.Length > 0 ? Result.Walk
                    : new[] { new WalkPoint { Name = "Вход", Feet = new Vector3(Result.Footprint.center.x, 0.05f, Result.Footprint.yMin - 3f) } };
                viewer.Configure(Result.Pivot, walk, Result.Orbit);
            }
        }

        void Teardown()
        {
            if (Result != null)
            {
                if (Result.House != null) Object.Destroy(Result.House);
                if (Result.Site != null) Object.Destroy(Result.Site);
                foreach (var m in Result.CreatedMaterials) if (m != null) Object.Destroy(m);
            }
            if (_writer != null)
                foreach (var m in _writer.RuntimeMeshes) if (m != null) Object.Destroy(m);
            _writer = null;
            Result = null;
        }
    }
}
