package libv2ray

import (
	"fmt"
	"net"
	"testing"
)

type testCoreCallbacks struct{}

func (testCoreCallbacks) Startup() int                 { return 0 }
func (testCoreCallbacks) Shutdown() int                { return 0 }
func (testCoreCallbacks) OnEmitStatus(int, string) int { return 0 }

func TestCoreStartsOnExplicitLoopbackPort(t *testing.T) {
	listener, err := net.Listen("tcp4", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	port := listener.Addr().(*net.TCPAddr).Port
	if err := listener.Close(); err != nil {
		t.Fatal(err)
	}

	config := fmt.Sprintf(`{
		"log":{"loglevel":"none"},
		"inbounds":[{"tag":"app-http","listen":"127.0.0.1","port":%d,"protocol":"http"}],
		"outbounds":[{"protocol":"blackhole"}]
	}`, port)
	controller := NewCoreController(testCoreCallbacks{})
	t.Cleanup(func() { _ = controller.StopLoop() })
	if err := controller.StartLoop(config, 0); err != nil {
		t.Fatal(err)
	}
	address := net.JoinHostPort("127.0.0.1", fmt.Sprint(port))
	conn, err := net.Dial("tcp4", address)
	if err != nil {
		t.Fatal(err)
	}
	_ = conn.Close()

	if err := controller.StopLoop(); err != nil {
		t.Fatal(err)
	}
	if conn, err := net.Dial("tcp4", address); err == nil {
		_ = conn.Close()
		t.Fatal("listener is still reachable after stopping Xray")
	}
}
