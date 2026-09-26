using System;
using System.Linq;
using UnityEngine;

namespace House4696.App.UI
{
    public enum AiState { NotConnected, Waiting, Online, Working }

    /// <summary>
    /// What the user's AI assistant is doing, for the status pill, the AI line and toasts:
    /// NotConnected (no client configured and never called) → Waiting (a client is configured, no call this session)
    /// → Online (called this session) ↔ Working (a call in flight or finished &lt; 12 s ago; held ≥ 1.5 s).
    /// </summary>
    public sealed class AiStatus
    {
        const float WorkingTail = 12f, MinWorking = 1.5f, ClientCheckEvery = 15f;

        readonly LocalApi _api;
        readonly AppSettings _settings;
        float _workingSince = -100f, _nextClientCheck;
        bool _clientConnected;

        public AiState State { get; private set; } = AiState.NotConnected;
        /// <summary>Verb phrase of the current/last command ("ИИ строит стены").</summary>
        public string Phrase { get; private set; } = "ИИ работает";
        public bool CalledThisSession => _api != null && _api.LastCallUtc != DateTime.MinValue;
        public DateTime LastCallUtc => _api?.LastCallUtc ?? DateTime.MinValue;
        public string LastCommand => _api?.LastCommand;
        public bool AnyClientConnected => _clientConnected;

        /// <summary>Raised when <see cref="State"/> or <see cref="Phrase"/> changes.</summary>
        public event Action Changed;
        /// <summary>Raised on the main thread after each answered command: command, success.</summary>
        public event Action<string, bool> CallFinished;
        /// <summary>The very first AI call ever on this computer.</summary>
        public event Action FirstCallEver;

        public AiStatus(LocalApi api, AppSettings settings)
        {
            _api = api;
            _settings = settings;
            if (_api != null)
                _api.CallFinished += (cmd, ok) =>
                {
                    if (!_settings.AiEverCalled)
                    {
                        _settings.AiEverCalled = true;
                        FirstCallEver?.Invoke();
                    }
                    CallFinished?.Invoke(cmd, ok);
                };
            RefreshClients();
        }

        /// <summary>Re-reads the AI clients' config files (after connecting one, or periodically).</summary>
        public void RefreshClients()
        {
            _nextClientCheck = Time.unscaledTime + ClientCheckEvery;
            try { _clientConnected = AiClients.All.Any(c => c.CanAutoConnect && AiClients.Status(c) == AiClients.Link.Connected); }
            catch (Exception) { _clientConnected = false; }
        }

        /// <summary>"Последний запрос: 2 мин назад" / "Запросов ещё не было".</summary>
        public string LastCallText => CalledThisSession ? "Последний запрос: " + Ui.Ago(LastCallUtc) : "Запросов ещё не было";

        public void Tick()
        {
            if (Time.unscaledTime > _nextClientCheck) RefreshClients();
            var next = Compute(out string phrase);
            if (next != State || phrase != Phrase)
            {
                State = next;
                Phrase = phrase;
                Changed?.Invoke();
            }
        }

        AiState Compute(out string phrase)
        {
            phrase = Verb(LastCommand);
            if (_api == null) return AiState.NotConnected;
            float now = Time.unscaledTime;
            bool busy = _api.InFlight > 0
                        || (_api.LastFinishedUtc != DateTime.MinValue && (DateTime.UtcNow - _api.LastFinishedUtc).TotalSeconds < WorkingTail);
            if (busy)
            {
                if (State != AiState.Working) _workingSince = now;
                return AiState.Working;
            }
            if (State == AiState.Working && now - _workingSince < MinWorking) return AiState.Working;
            if (CalledThisSession) return AiState.Online;
            if (_clientConnected || _settings.AiEverCalled) return AiState.Waiting;
            return AiState.NotConnected;
        }

        /// <summary>Human phrase for an API command.</summary>
        public static string Verb(string command)
        {
            switch (command)
            {
                case "exterior_walls": return "ИИ строит стены";
                case "upsert": return "ИИ вносит правки";
                case "remove": return "ИИ убирает элементы";
                case "replace_project": return "ИИ перестраивает дом";
                case "create_project": return "ИИ создаёт проект";
                case "open_project": return "ИИ открывает проект";
                case "render": return "ИИ смотрит на дом";
                case "validate": return "ИИ проверяет проект";
                case "undo": return "ИИ отменяет правку";
                case "catalog": return "ИИ выбирает мебель";
                case "materials": return "ИИ подбирает отделку";
                case "measure": return "ИИ делает замеры";
                case "get_project": case "summary": case "status": case "list_projects": return "ИИ изучает проект";
                default: return "ИИ работает";
            }
        }

        /// <summary>Commands that change the house (toasts with undo).</summary>
        public static bool IsEdit(string command) =>
            command == "exterior_walls" || command == "upsert" || command == "remove" || command == "replace_project";

        /// <summary>Toast text after a finished edit.</summary>
        public static string EditToast(string command) => command switch
        {
            "exterior_walls" => "ИИ построил наружные стены",
            "replace_project" => "ИИ перестроил дом",
            "remove" => "ИИ убрал элементы",
            _ => "ИИ внёс правку",
        };
    }
}
