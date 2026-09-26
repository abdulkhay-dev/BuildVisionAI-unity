using System;
using System.Collections;
using System.IO;
using UnityEngine;

namespace House4696.App
{
    /// <summary>
    /// Snapshots of the current view at high resolution (≈4K wide, the window's aspect) saved as PNG to
    /// <c>~/Pictures/House</c> — for sharing a view of the house.
    /// </summary>
    public sealed class Snapshots
    {
        public const int Width = 3840;

        readonly HouseSession _session;
        readonly ViewRenderer _renderer;
        readonly HouseLighting _lighting;

        public bool Busy { get; private set; }

        public Snapshots(HouseSession session, ViewRenderer renderer, HouseLighting lighting)
        {
            _session = session; _renderer = renderer; _lighting = lighting;
        }

        public static string Folder => Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.MyPictures), "House");

        /// <summary>Renders and saves; <paramref name="done"/> gets the file path, <paramref name="fail"/> a message.</summary>
        public IEnumerator Capture(Action<string> done, Action<string> fail)
        {
            if (Busy || !_session.HasProject) yield break;
            Busy = true;
            try
            {
                if (_lighting != null) yield return _lighting.WaitForBake(60f);
                float aspect = Screen.height > 0 ? (float)Screen.width / Screen.height : 16f / 9f;
                var q = new RenderRequest { Mode = RenderMode.Current, Width = Width, Height = Mathf.RoundToInt(Width / aspect), Frames = 8 };
                byte[] png = null;
                string error = null;
                yield return _renderer.Render(q, b => png = b, e => error = e);
                if (png == null) { fail(error ?? "не удалось сделать снимок"); yield break; }
                string name = Safe(_session.Doc.Meta?.Name ?? _session.ProjectId) + " " + DateTime.Now.ToString("yyyy-MM-dd HH.mm.ss") + ".png";
                string path = Path.Combine(Folder, name);
                try
                {
                    Directory.CreateDirectory(Folder);
                    File.WriteAllBytes(path, png);
                }
                catch (Exception e) { fail(e.Message); yield break; }
                done(path);
            }
            finally { Busy = false; }
        }

        static string Safe(string s)
        {
            foreach (char c in Path.GetInvalidFileNameChars()) s = s.Replace(c, '-');
            return s.Replace(':', '-').Trim();
        }
    }
}
