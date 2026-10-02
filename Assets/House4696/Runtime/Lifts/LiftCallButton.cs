using House4696.Runtime;
using UnityEngine;

namespace House4696.Lifts
{
    /// <summary>A landing's call button panel (and its door leaves): calls the car to that stop or opens its doors.</summary>
    public sealed class LiftCallButton : MonoBehaviour, IInteractable
    {
        public LiftController Lift;
        public int Stop;
        public string Prompt => Lift != null ? Lift.CallPrompt(Stop) : null;
        public void Interact()
        {
            if (Lift == null) return;
            if (Stop == Lift.Current && !Lift.Moving) Lift.ToggleDoors();
            else Lift.Call(Stop);
        }
    }
}
