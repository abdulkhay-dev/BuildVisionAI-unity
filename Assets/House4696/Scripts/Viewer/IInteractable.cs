namespace House4696.Runtime
{
    /// <summary>
    /// Something in the house the walker uses by looking at it and pressing E (or clicking it): a lift's call button,
    /// its car operating panel, its doors. Checked before plain <see cref="Door"/>s.
    /// </summary>
    public interface IInteractable
    {
        /// <summary>The hint shown while looking at it ("E — вызвать лифт"); null = nothing to do now.</summary>
        string Prompt { get; }
        void Interact();
    }
}
