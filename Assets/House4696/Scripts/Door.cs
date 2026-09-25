using UnityEngine;

namespace House4696.Runtime
{
    /// <summary>Hinged door: sits on a pivot at the hinge line and swings by <see cref="OpenAngle"/> around Y.</summary>
    public sealed class Door : MonoBehaviour
    {
        [SerializeField] float openAngle = 95f;
        [SerializeField, Tooltip("Full swings per second")] float speed = 1.6f;

        Quaternion _closed;
        float _t;       // 0 = closed, 1 = open
        bool _open;

        public float OpenAngle { get => openAngle; set => openAngle = value; }
        public bool IsOpen => _open;

        public void Toggle() => _open = !_open;

        void Awake() => _closed = transform.localRotation;

        void Update()
        {
            float target = _open ? 1f : 0f;
            if (Mathf.Approximately(_t, target)) return;
            _t = Mathf.MoveTowards(_t, target, speed * Time.deltaTime);
            transform.localRotation = _closed * Quaternion.Euler(0f, openAngle * Mathf.SmoothStep(0f, 1f, _t), 0f);
        }
    }
}
