using System.IO;
using UnityEngine;
using UnityEngine.UIElements;

namespace House4696.Experiments
{
    /// <summary>
    /// Screenshots of the app with its UI in Play mode (the unfocused editor writes no ScreenCapture): the camera is
    /// rendered into a texture, the UI panel draws over it on the next frame, then <see cref="End"/> saves the PNG.
    /// </summary>
    public static class UiShot
    {
        static RenderTexture _rt;
        static PanelSettings _panel;
        static string _path;

        public static string Begin(string path, int w = 1600, int h = 940)
        {
            var doc = Object.FindAnyObjectByType<UIDocument>();
            var cam = Camera.main;
            if (doc == null || cam == null) return "no UI or camera";
            _path = path;
            _rt = new RenderTexture(w, h, 24, RenderTextureFormat.ARGB32, RenderTextureReadWrite.sRGB);
            cam.targetTexture = _rt;
            cam.Render();
            cam.targetTexture = null;
            _panel = doc.panelSettings;
            _panel.clearColor = false;
            _panel.targetTexture = _rt;
            return "ok";
        }

        public static string End()
        {
            if (_rt == null) return "no shot";
            var prev = RenderTexture.active;
            RenderTexture.active = _rt;
            var tex = new Texture2D(_rt.width, _rt.height, TextureFormat.RGB24, false);
            tex.ReadPixels(new Rect(0, 0, _rt.width, _rt.height), 0, 0);
            tex.Apply();
            RenderTexture.active = prev;
            Directory.CreateDirectory(Path.GetDirectoryName(_path) ?? ".");
            File.WriteAllBytes(_path, tex.EncodeToPNG());
            Object.DestroyImmediate(tex);
            _panel.targetTexture = null;
            _rt.Release();
            Object.DestroyImmediate(_rt);
            _rt = null;
            return _path;
        }
    }
}
