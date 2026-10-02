using House4696.Runtime;
using UnityEngine;

namespace House4696.Lifts
{
    /// <summary>The car operating panel: a menu of the stops.</summary>
    public sealed class LiftCarPanel : MonoBehaviour, IInteractable
    {
        public LiftController Lift;
        public string Prompt => Lift != null ? Lift.PanelPrompt : null;
        public void Interact() { if (Lift != null && !Lift.Moving) Lift.RequestFloorPick(); }
    }
}
