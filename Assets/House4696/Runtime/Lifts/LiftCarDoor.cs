using House4696.Runtime;
using UnityEngine;

namespace House4696.Lifts
{
    /// <summary>The car's door leaves: open or close the doors where the car stands.</summary>
    public sealed class LiftCarDoor : MonoBehaviour, IInteractable
    {
        public LiftController Lift;
        public string Prompt => Lift == null || Lift.Moving ? null : Lift.DoorsOpen ? "E — закрыть двери лифта" : "E — открыть двери лифта";
        public void Interact() { if (Lift != null) Lift.ToggleDoors(); }
    }
}
