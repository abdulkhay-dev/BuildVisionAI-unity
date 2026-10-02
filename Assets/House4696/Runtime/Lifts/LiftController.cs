using System;
using System.Collections.Generic;
using House4696.Runtime;
using UnityEngine;

namespace House4696.Lifts
{
    /// <summary>
    /// A working lift in the built house: call buttons at the landings, the car operating panel (a floor menu), doors that
    /// open together at the stop where the car is and stay open while someone stands in the doorway, the car riding
    /// between the stops at the catalogue speed with soft acceleration — carrying the walker standing in it — and the
    /// counterweight and ropes moving with it. Runs before the viewer (the camera follows a carried walker in the same
    /// frame).
    /// </summary>
    [DefaultExecutionOrder(-50)]
    public sealed class LiftController : MonoBehaviour
    {
        /// <summary>Raised when someone uses the car operating panel: the app shows a menu of the stops (see AppUI).</summary>
        public static event Action<LiftController> FloorPickRequested;

        public sealed class Leaf { public Transform T; public Vector3 Closed, Slide; }

        public string LiftId, Title;
        /// <summary>Floor heights and names of the stops (low → high).</summary>
        public float[] StopY;
        public string[] StopNames;
        /// <summary>The car (meshes built at <see cref="ParkedY"/>), what follows it (its light and probe), the counterweight.</summary>
        public Transform Car, Counterweight;
        public readonly List<Transform> Followers = new List<Transform>();
        public float ParkedY;
        /// <summary>Ropes: unit meshes hanging from <see cref="RopeTop"/>, scaled to reach the car's / counterweight's top.</summary>
        public Transform CarRopes, CwRopes;
        public float RopeTop, CarRopeBottom0, CwRopeBottom0;
        public float Speed = 1f, Accel = 0.7f, OpenTime = 1.6f, Dwell = 5f;
        /// <summary>World → lift-local (x across the doors, z towards the hall), the car's plan box and height, the doorway.</summary>
        public Matrix4x4 ToLocal;
        public Rect CarBox;
        public float CarHeight;
        public float DoorX0, DoorX1, DoorZ0;
        public List<Leaf>[] Landing;
        public readonly List<Leaf> CarLeaves = new List<Leaf>();
        public ReflectionProbe Probe;

        enum State { Idle, Moving, Opening, Open, Closing }
        State _state;
        float _y, _v, _door, _timer;
        int _target = -1;
        readonly List<int> _queue = new List<int>();
        Vector3 _carBase, _cwBase;
        readonly List<Vector3> _followBase = new List<Vector3>();
        CharacterController _walker;
        float _findWalker;

        /// <summary>The stop the car is at (or left last).</summary>
        public int Current { get; private set; }
        public bool Moving => _state == State.Moving;
        public bool DoorsOpen => _door > 0.5f;

        /// <summary>Starts at <paramref name="stop"/>; open doors stay open until someone calls the lift.</summary>
        public void Init(int stop, bool open)
        {
            Current = Mathf.Clamp(stop, 0, StopY.Length - 1);
            _y = StopY[Current];
            _carBase = Car != null ? Car.position : Vector3.zero;
            _cwBase = Counterweight != null ? Counterweight.position : Vector3.zero;
            _followBase.Clear();
            foreach (var f in Followers) _followBase.Add(f != null ? f.position : Vector3.zero);
            _door = open ? 1f : 0f;
            _state = open ? State.Open : State.Idle;
            _timer = open ? float.PositiveInfinity : 0f;
            Apply();
        }

        // ------------------------------------------------------------------ requests
        /// <summary>A call from a landing (or the panel): the car comes, or opens its doors when it is already there.</summary>
        public void Call(int stop)
        {
            if (stop < 0 || stop >= StopY.Length) return;
            if (_state == State.Moving && _target == stop) return;
            if (stop == Current && _state != State.Moving)
            {
                if (_state == State.Idle || _state == State.Closing) _state = State.Opening;
                else if (_state == State.Open) _timer = Dwell;
                return;
            }
            if (!_queue.Contains(stop)) _queue.Add(stop);
            // a car waiting with open doors leaves soon
            if (_state == State.Open) _timer = Mathf.Min(_timer, 1.2f);
        }

        /// <summary>The doors at the car's stop: open them, or close them now.</summary>
        public void ToggleDoors()
        {
            if (_state == State.Moving) return;
            if (_state == State.Open || _state == State.Opening) { _state = State.Closing; _timer = 0f; }
            else _state = State.Opening;
        }

        /// <summary>The car operating panel: a floor menu in the app, or the next stop when nothing shows menus.</summary>
        public void RequestFloorPick()
        {
            if (FloorPickRequested != null) FloorPickRequested(this);
            else Call(Current + 1 < StopY.Length ? Current + 1 : 0);
        }

        public string CallPrompt(int stop)
        {
            if (_state == State.Moving) return _target == stop ? "Лифт едет сюда…" : "E — вызвать лифт (он в пути)";
            if (stop == Current) return DoorsOpen ? "E — закрыть двери лифта" : "E — открыть двери лифта";
            return _queue.Contains(stop) ? "Лифт вызван…" : $"E — вызвать лифт (кабина: {StopNames[Current]})";
        }

        public string PanelPrompt => _state == State.Moving ? $"Лифт едет: {StopNames[_target]}" : "E — выбрать этаж";

        // ------------------------------------------------------------------ motion
        void Update()
        {
            float dt = Mathf.Min(Time.deltaTime, 0.05f);
            if (StopY == null || StopY.Length == 0) return;
            float carBefore = _y;
            switch (_state)
            {
                case State.Idle:
                    if (_queue.Count > 0)
                    {
                        _target = _queue[0];
                        _queue.RemoveAt(0);
                        _state = _target == Current ? State.Opening : State.Moving;
                        _v = 0f;
                    }
                    break;
                case State.Moving:
                {
                    float d = StopY[_target] - _y, dist = Mathf.Abs(d), dir = Mathf.Sign(d);
                    float brake = _v * _v / (2f * Accel);
                    _v = dist <= brake + 0.005f ? Mathf.Max(0.05f, _v - Accel * dt) : Mathf.Min(Speed, _v + Accel * dt);
                    float step = _v * dt;
                    if (step >= dist)
                    {
                        _y = StopY[_target];
                        _v = 0f;
                        Current = _target;
                        _target = -1;
                        _state = State.Opening;
                        if (Probe != null) Probe.RenderProbe();
                    }
                    else _y += dir * step;
                    break;
                }
                case State.Opening:
                    _door = Mathf.Min(1f, _door + dt / OpenTime);
                    if (_door >= 1f) { _state = State.Open; _timer = _queue.Count > 0 ? 1.5f : Dwell; }
                    break;
                case State.Open:
                    _timer -= dt;
                    if (_queue.Count > 0) _timer = Mathf.Min(_timer, 1.5f);
                    if (_timer <= 0f && !InDoorway()) _state = State.Closing;
                    break;
                case State.Closing:
                    if (InDoorway()) { _state = State.Opening; break; }
                    _door = Mathf.Max(0f, _door - dt / OpenTime);
                    if (_door <= 0f) _state = State.Idle;
                    break;
            }
            float dy = _y - carBefore;
            if (dy != 0f && WalkerInCar(carBefore)) Carry(dy);
            // a lift standing still with its doors at rest changes nothing: no transforms, no physics sync
            if (_y == _appliedY && _door == _appliedDoor && Current == _appliedStop) return;
            Apply();
        }

        float _appliedY = float.NaN, _appliedDoor = float.NaN;
        int _appliedStop = -1;

        /// <summary>Car, counterweight, ropes, followers and the door leaves of the car's stop to the current state.</summary>
        void Apply()
        {
            float off = _y - ParkedY;
            if (Car != null) Car.position = _carBase + Vector3.up * off;
            for (int i = 0; i < Followers.Count; i++) if (Followers[i] != null) Followers[i].position = _followBase[i] + Vector3.up * off;
            if (Counterweight != null) Counterweight.position = _cwBase - Vector3.up * off;
            if (CarRopes != null) CarRopes.localScale = new Vector3(1f, Mathf.Max(0.01f, RopeTop - (CarRopeBottom0 + off)), 1f);
            if (CwRopes != null) CwRopes.localScale = new Vector3(1f, Mathf.Max(0.01f, RopeTop - (CwRopeBottom0 - off)), 1f);
            float t = _door * _door * (3f - 2f * _door);
            foreach (var l in CarLeaves) l.T.localPosition = l.Closed + l.Slide * t;
            if (Landing != null)
                for (int s = 0; s < Landing.Length; s++)
                {
                    float ts = s == Current && _state != State.Moving ? t : 0f;
                    foreach (var l in Landing[s]) l.T.localPosition = l.Closed + l.Slide * ts;
                }
            Physics.SyncTransforms();
            _appliedY = _y; _appliedDoor = _door; _appliedStop = Current;
        }

        // ------------------------------------------------------------------ the walker
        CharacterController Walker()
        {
            if (_walker != null) return _walker;
            if (Time.time < _findWalker) return null;
            _findWalker = Time.time + 1f;
            _walker = FindFirstObjectByType<CharacterController>();
            return _walker;
        }

        bool WalkerInCar(float carY)
        {
            var w = Walker();
            if (w == null || !w.enabled) return false;
            var p = ToLocal.MultiplyPoint3x4(w.transform.position);
            return p.x > CarBox.xMin - 0.05f && p.x < CarBox.xMax + 0.05f && p.z > CarBox.yMin - 0.05f && p.z < CarBox.yMax + 0.15f
                   && p.y > carY - 0.4f && p.y < carY + CarHeight;
        }

        void Carry(float dy)
        {
            var w = _walker;
            w.enabled = false;
            w.transform.position += Vector3.up * dy;
            w.enabled = true;
        }

        /// <summary>Someone stands between the doors of the car's stop (the doors wait for them).</summary>
        bool InDoorway()
        {
            var w = Walker();
            if (w == null || !w.enabled) return false;
            var p = ToLocal.MultiplyPoint3x4(w.transform.position);
            float y = StopY[Current];
            return p.x > DoorX0 - 0.15f && p.x < DoorX1 + 0.15f && p.z > DoorZ0 - 0.35f && p.z < 0.3f && p.y > y - 0.3f && p.y < y + 1.2f;
        }
    }
}
