using System;
using UnityEngine;

namespace House4696.App
{
    public enum GraphicsQuality { Fast, Balanced, Max }

    public enum ProjectSort { Recent, Name, Area }

    /// <summary>User preferences and first-run progress of the app (PlayerPrefs). Changes raise <see cref="Changed"/>.</summary>
    public sealed class AppSettings
    {
        public event Action Changed;

        static bool GetBool(string key, bool def) => PlayerPrefs.GetInt(key, def ? 1 : 0) == 1;
        void SetBool(string key, bool value)
        {
            if (GetBool(key, !value) == value && PlayerPrefs.HasKey(key)) return;
            PlayerPrefs.SetInt(key, value ? 1 : 0);
            Changed?.Invoke();
        }

        public GraphicsQuality Quality
        {
            get => (GraphicsQuality)Mathf.Clamp(PlayerPrefs.GetInt("house.quality", (int)GraphicsQuality.Balanced), 0, 2);
            set { PlayerPrefs.SetInt("house.quality", (int)value); Changed?.Invoke(); }
        }

        public ProjectSort Sort
        {
            get => (ProjectSort)Mathf.Clamp(PlayerPrefs.GetInt("house.sort", 0), 0, 2);
            set { PlayerPrefs.SetInt("house.sort", (int)value); Changed?.Invoke(); }
        }

        /// <summary>Pixels rendered per frame in Balanced (millions); STP reconstructs the rest.</summary>
        public static float BalancedMegapixels = 1.4f;

        public bool ShowStats { get => GetBool("house.showStats", false); set => SetBool("house.showStats", value); }
        /// <summary>Control hints after a mode switch (coach strip).</summary>
        public bool ShowHints { get => GetBool("house.showHints", true); set => SetBool("house.showHints", value); }
        /// <summary>The plan panel opens by itself in walk/fly (and in orbit) mode.</summary>
        public bool PlanInWalk { get => GetBool("house.planInWalk", true); set => SetBool("house.planInWalk", value); }
        public bool PlanInOrbit { get => GetBool("house.planInOrbit", false); set => SetBool("house.planInOrbit", value); }

        // first-run progress (Home checklist, one-time hints)
        public bool AiEverCalled { get => GetBool("house.aiEverCalled", false); set => SetBool("house.aiEverCalled", value); }
        public bool AiBuiltOnce { get => GetBool("house.aiBuiltOnce", false); set => SetBool("house.aiBuiltOnce", value); }
        public bool WalkedOnce { get => GetBool("house.walkedOnce", false); set => SetBool("house.walkedOnce", value); }
        public bool ChecklistDismissed { get => GetBool("house.checklistDismissed", false); set => SetBool("house.checklistDismissed", value); }
        public bool CleanViewHintShown { get => GetBool("house.cleanViewHint", false); set => SetBool("house.cleanViewHint", value); }

        /// <summary>
        /// Pixels rendered per frame (millions); a larger screen is rendered smaller and upscaled with FSR.
        /// <see cref="float.PositiveInfinity"/> = always native resolution.
        /// </summary>
        public float TargetMegapixels => Quality switch
        {
            GraphicsQuality.Fast => 0.9f,
            GraphicsQuality.Max => 2.6f,
            _ => BalancedMegapixels,
        };

        /// <summary>
        /// Upscaler of the preset: STP (temporal: sharper, cleaner fine detail such as cladding and leaves) for
        /// Balanced/Max; FSR1 with SMAA for Fast (cheapest). MSAA stays off in the viewer: STP needs it off, and on
        /// alpha-tested foliage it cost ~6 ms for no visible gain over SMAA.
        /// </summary>
        public bool UseStp => Quality != GraphicsQuality.Fast;

        public static string Title(GraphicsQuality q) => q switch
        {
            GraphicsQuality.Fast => "Быстро",
            GraphicsQuality.Max => "Максимум",
            _ => "Баланс",
        };

        public static string Hint(GraphicsQuality q) => q switch
        {
            GraphicsQuality.Fast => "Плавно даже на ноутбуке, картинка мягче",
            GraphicsQuality.Max => "Максимальная чёткость для показа и снимков",
            _ => "Чёткость и плавность — рекомендуем",
        };

        public static string Title(ProjectSort s) => s switch
        {
            ProjectSort.Name => "По названию",
            ProjectSort.Area => "По площади",
            _ => "Сначала недавние",
        };
    }
}
