using UnityEditor;

namespace House4696
{
    /// <summary>
    /// The MCP client of this machine is configured for the stdio transport, while the
    /// MCP for Unity package defaults to HTTP. Start the stdio bridge once per editor session.
    /// </summary>
    [InitializeOnLoad]
    static class McpStdioBoot
    {
        static McpStdioBoot()
        {
            EditorApplication.delayCall += () =>
            {
                if (!MCPForUnity.Editor.Services.Transport.Transports.StdioBridgeHost.IsRunning)
                    MCPForUnity.Editor.McpCiBoot.StartStdioForCi();
            };
        }
    }
}
