using UnityEngine;

namespace House4696.Runtime
{
    /// <summary>How a door's moving part moves.</summary>
    public enum DoorMotion
    {
        /// <summary>Turns about the hinge line (Y) by <see cref="Door.OpenAngle"/>.</summary>
        Swing,
        /// <summary>Runs along its rail by <see cref="Door.SlideBy"/> (local offset when open).</summary>
        Slide,
        /// <summary>
        /// Book fold: this pivot (at the jamb) turns by <see cref="Door.OpenAngle"/>, <see cref="Door.FoldSecond"/> (the pivot
        /// between the two panels, a child of this one) by -2 × <see cref="Door.OpenAngle"/>, so the free edge stays on the track.
        /// </summary>
        Fold,
    }

    /// <summary>
    /// A door's moving part: sits on a pivot and opens by <see cref="Motion"/>. Leaves of one door (a double door, the two
    /// books of a folding door, the two leaves of a coupe) name each other as <see cref="Partner"/> and open together.
    /// </summary>
    public sealed class Door : MonoBehaviour
    {
        [SerializeField] float openAngle = 95f;
        [SerializeField, Tooltip("Full openings per second")] float speed = 1.6f;
        public DoorMotion Motion = DoorMotion.Swing;
        [Tooltip("Slide: local offset of the leaf when fully open.")]
        public Vector3 SlideBy;
        [Tooltip("Fold: the pivot between the two panels (a child of this pivot).")]
        public Transform FoldSecond;
        [Tooltip("The other leaf of the same door: opens and closes with this one.")]
        public Door Partner;

        Quaternion _closed, _closedSecond;
        Vector3 _closedPos;
        bool _hasClosed;
        float _t;       // 0 = closed, 1 = open
        bool _open;

        public float OpenAngle { get => openAngle; set => openAngle = value; }
        public bool IsOpen => _open;

        public void Toggle() => SetOpen(!_open);

        /// <summary>Opens or closes the door (and its partner); <paramref name="instant"/> skips the animation.</summary>
        public void SetOpen(bool open, bool instant = false) => Set(open, instant, true);

        void Set(bool open, bool instant, bool withPartner)
        {
            CaptureClosed();
            _open = open;
            if (instant)
            {
                _t = open ? 1f : 0f;
                Apply();
            }
            if (withPartner && Partner != null && Partner != this) Partner.Set(open, instant, false);
        }

        // the closed pose is the one the generator built (captured before the first move; editor builds have no Awake)
        void CaptureClosed()
        {
            if (_hasClosed) return;
            _closed = transform.localRotation;
            _closedPos = transform.localPosition;
            if (FoldSecond != null) _closedSecond = FoldSecond.localRotation;
            _hasClosed = true;
        }

        void Awake() => CaptureClosed();

        void Apply()
        {
            float k = Mathf.SmoothStep(0f, 1f, _t);
            switch (Motion)
            {
                case DoorMotion.Slide:
                    transform.localPosition = _closedPos + SlideBy * k;
                    break;
                case DoorMotion.Fold:
                    transform.localRotation = _closed * Quaternion.Euler(0f, openAngle * k, 0f);
                    if (FoldSecond != null) FoldSecond.localRotation = _closedSecond * Quaternion.Euler(0f, -2f * openAngle * k, 0f);
                    break;
                default:
                    transform.localRotation = _closed * Quaternion.Euler(0f, openAngle * k, 0f);
                    break;
            }
        }

        void Update()
        {
            float target = _open ? 1f : 0f;
            if (Mathf.Approximately(_t, target)) return;
            _t = Mathf.MoveTowards(_t, target, speed * Time.deltaTime);
            Apply();
        }
    }
}
