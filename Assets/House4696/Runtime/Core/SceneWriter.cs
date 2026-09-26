using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Rendering;

namespace House4696.Core
{
    /// <summary>
    /// Editor-side persistence of generated content. At runtime there are no hooks: meshes live in memory and
    /// static flags do not exist. In the editor the hooks store meshes in an asset and set static editor flags.
    /// </summary>
    public interface ISceneWriterHooks
    {
        void StoreMesh(Mesh mesh);
        void MarkStatic(GameObject go, bool probeStatic);
        void MarkDynamic(GameObject go);
    }

    /// <summary>Creates scene objects from <see cref="MeshBuilder"/>s; works both in the editor and in a player.</summary>
    public sealed class SceneWriter
    {
        readonly ISceneWriterHooks _hooks;
        readonly HashSet<string> _names = new HashSet<string>();
        readonly List<Mesh> _runtimeMeshes = new List<Mesh>();

        /// <summary>Meshes created without editor hooks (in memory): the owner destroys them when the house is rebuilt.</summary>
        public IReadOnlyList<Mesh> RuntimeMeshes => _runtimeMeshes;

        public SceneWriter(ISceneWriterHooks hooks = null) { _hooks = hooks; }

        public Transform Group(string name, Transform parent)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            return go.transform;
        }

        /// <summary>Gives the mesh a unique name and hands it to the editor hooks (if any).</summary>
        public Mesh Store(Mesh mesh)
        {
            string n = mesh.name;
            int i = 1;
            while (!_names.Add(n)) n = mesh.name + "_" + (++i);
            mesh.name = n;
            if (_hooks != null) _hooks.StoreMesh(mesh); else _runtimeMeshes.Add(mesh);
            return mesh;
        }

        public GameObject Emit(string name, Transform parent, MeshBuilder mb, bool castShadows = true, bool probeStatic = false)
        {
            if (mb == null || mb.IsEmpty) return null;
            var mesh = Store(mb.Build(name));
            return Instance(name, parent, mesh, mb.Materials, castShadows, probeStatic);
        }

        public GameObject Instance(string name, Transform parent, Mesh mesh, Material[] materials, bool castShadows = true,
                                   bool probeStatic = false)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            go.AddComponent<MeshFilter>().sharedMesh = mesh;
            var mr = go.AddComponent<MeshRenderer>();
            mr.sharedMaterials = materials;
            mr.shadowCastingMode = castShadows ? ShadowCastingMode.On : ShadowCastingMode.Off;
            mr.receiveShadows = true;
            _hooks?.MarkStatic(go, probeStatic);
            return go;
        }

        /// <summary>Objects that move at runtime (door leaves) must not be static.</summary>
        public void MarkDynamic(GameObject go) => _hooks?.MarkDynamic(go);

        /// <summary>
        /// Destroys the in-memory meshes this writer made for the objects under <paramref name="root"/> (an item that is
        /// rebuilt or a preview that is dropped); meshes of library prefabs are assets and stay.
        /// </summary>
        public void Release(GameObject root)
        {
            if (root == null) return;
            foreach (var mf in root.GetComponentsInChildren<MeshFilter>(true))
            {
                var mesh = mf.sharedMesh;
                if (mesh == null || !_runtimeMeshes.Remove(mesh)) continue;
                if (Application.isPlaying) Object.Destroy(mesh); else Object.DestroyImmediate(mesh);
            }
        }
    }
}
