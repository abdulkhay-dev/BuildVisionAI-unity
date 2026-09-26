using System;
using System.Collections;
using System.Reflection;
using Newtonsoft.Json;
using Newtonsoft.Json.Converters;
using Newtonsoft.Json.Serialization;
using UnityEngine;

namespace House4696.Model
{
    /// <summary>
    /// JSON (de)serialisation of <see cref="HouseDocument"/>: camelCase names, enums as camelCase strings, vectors
    /// as arrays (<c>[x, z]</c> / <c>[x, y, z]</c>), nulls and empty lists omitted to keep files short.
    /// </summary>
    public static class HouseJson
    {
        public static readonly JsonSerializerSettings Settings = new JsonSerializerSettings
        {
            ContractResolver = new CompactResolver(),
            NullValueHandling = NullValueHandling.Ignore,
            Formatting = Formatting.Indented,
            FloatFormatHandling = FloatFormatHandling.DefaultValue,
            Converters =
            {
                new StringEnumConverter(new CamelCaseNamingStrategy()),
                new Vector2Converter(),
                new Vector3Converter(),
                new FloatConverter(),
            },
        };

        public static string Serialize(HouseDocument doc) => JsonConvert.SerializeObject(doc, Settings);

        public static HouseDocument Deserialize(string json)
        {
            var doc = JsonConvert.DeserializeObject<HouseDocument>(json, Settings);
            if (doc == null) throw new FormatException("empty house document");
            return doc;
        }

        /// <summary>Round-trips a document (deep copy).</summary>
        public static HouseDocument Clone(HouseDocument doc) => Deserialize(Serialize(doc));

        /// <summary>Deep copy of a part of a document (an item, a level…) through the same JSON form.</summary>
        public static T Copy<T>(T part) where T : class =>
            part == null ? null : JsonConvert.DeserializeObject<T>(JsonConvert.SerializeObject(part, Settings), Settings);

        sealed class CompactResolver : CamelCasePropertyNamesContractResolver
        {
            protected override JsonProperty CreateProperty(MemberInfo member, MemberSerialization memberSerialization)
            {
                var p = base.CreateProperty(member, memberSerialization);
                if (typeof(ICollection).IsAssignableFrom(p.PropertyType))
                    p.ShouldSerialize = o => p.ValueProvider.GetValue(o) is ICollection c && c.Count > 0;
                return p;
            }
        }

        /// <summary>Floats are written with 4 decimals (millimetre precision is plenty, and files stay diff-friendly).</summary>
        sealed class FloatConverter : JsonConverter
        {
            public override bool CanConvert(Type t) => t == typeof(float) || t == typeof(float?);
            public override bool CanRead => false;
            public override object ReadJson(JsonReader r, Type t, object existing, JsonSerializer s) => throw new NotSupportedException();
            public override void WriteJson(JsonWriter w, object value, JsonSerializer s)
            {
                if (value == null) w.WriteNull(); else w.WriteValue(Math.Round((float)value, 4));
            }
        }

        /// <summary>Vector as a JSON number array; also handles the nullable form.</summary>
        abstract class VectorConverter<T> : JsonConverter where T : struct
        {
            protected abstract int Size { get; }
            protected abstract float[] ToArray(T v);
            protected abstract T FromArray(float[] a);

            public override bool CanConvert(Type t) => t == typeof(T) || t == typeof(T?);

            public override void WriteJson(JsonWriter w, object value, JsonSerializer s)
            {
                if (value == null) { w.WriteNull(); return; }
                w.WriteStartArray();
                foreach (var f in ToArray((T)value)) w.WriteValue(Math.Round(f, 4));
                w.WriteEndArray();
            }

            public override object ReadJson(JsonReader r, Type t, object existing, JsonSerializer s)
            {
                if (r.TokenType == JsonToken.Null) return t == typeof(T?) ? null : (object)default(T);
                var a = s.Deserialize<float[]>(r);
                if (a == null || a.Length != Size)
                    throw new JsonSerializationException($"expected an array of {Size} numbers at {r.Path}");
                return FromArray(a);
            }
        }

        sealed class Vector2Converter : VectorConverter<Vector2>
        {
            protected override int Size => 2;
            protected override float[] ToArray(Vector2 v) => new[] { v.x, v.y };
            protected override Vector2 FromArray(float[] a) => new Vector2(a[0], a[1]);
        }

        sealed class Vector3Converter : VectorConverter<Vector3>
        {
            protected override int Size => 3;
            protected override float[] ToArray(Vector3 v) => new[] { v.x, v.y, v.z };
            protected override Vector3 FromArray(float[] a) => new Vector3(a[0], a[1], a[2]);
        }
    }
}
