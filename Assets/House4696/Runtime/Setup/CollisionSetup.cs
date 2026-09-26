using UnityEngine;

namespace House4696.Setup
{
    /// <summary>
    /// Adds colliders to the generated scene so it can be walked through: exact mesh colliders for
    /// architecture and hardscape, cheap primitives for vegetation, nothing for soft decor (grass, curtains).
    /// Rules are matched by object-name prefix, first match wins.
    /// </summary>
    public static class CollisionSetup
    {
        enum Shape { None, Mesh, Box, Trunk }

        static readonly (string prefix, Shape shape)[] Rules =
        {
            ("Curtains_", Shape.None),
            ("Water_", Shape.None),            // stream water: you wade through it to the bed
            ("Decor_", Shape.None),
            ("Lawn_Blades", Shape.None),
            ("Plant_", Shape.None),
            ("Pot_Grass", Shape.None),
            ("Lawn", Shape.Box),
            ("Model_", Shape.Box),            // library furniture: a box is enough to walk around it
            ("Hedge_", Shape.Box),
            ("Spruce", Shape.Trunk),
            ("Birch", Shape.Trunk),
            ("Broadleaf", Shape.Trunk),
        };

        const float TrunkRadius = 0.3f, TrunkHeight = 4f;

        public static int Apply(params GameObject[] roots)
        {
            int count = 0;
            foreach (var root in roots)
            foreach (var mf in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if (mf.sharedMesh == null || mf.GetComponent<Collider>() != null) continue;
                if (Add(mf, ShapeFor(mf.name))) count++;
            }
            return count;
        }

        static Shape ShapeFor(string name)
        {
            // coarse LODs and shadow-only proxies duplicate a collider their full-detail sibling already has
            if (name.EndsWith("_LOD1", System.StringComparison.Ordinal) || name.EndsWith("_Shadow", System.StringComparison.Ordinal)
                || name == "ShadowProxy") return Shape.None;
            foreach (var (prefix, shape) in Rules)
                if (name.StartsWith(prefix, System.StringComparison.Ordinal)) return shape;
            return Shape.Mesh;
        }

        static bool Add(MeshFilter mf, Shape shape)
        {
            var go = mf.gameObject;
            switch (shape)
            {
                case Shape.Mesh:
                    go.AddComponent<MeshCollider>().sharedMesh = mf.sharedMesh;
                    return true;
                case Shape.Box:
                    go.AddComponent<BoxCollider>(); // auto-fits the mesh bounds
                    return true;
                case Shape.Trunk:
                    // trees are uniformly scaled instances with the trunk at the local origin
                    float s = Mathf.Max(go.transform.lossyScale.y, 0.01f);
                    var c = go.AddComponent<CapsuleCollider>();
                    c.direction = 1;
                    c.radius = TrunkRadius / s;
                    c.height = TrunkHeight / s;
                    c.center = new Vector3(0, TrunkHeight * 0.5f / s, 0);
                    return true;
                default:
                    return false;
            }
        }
    }
}
