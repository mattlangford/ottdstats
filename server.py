
import servercontroller

class OpenTTDStatsServer:

    @staticmethod
    def main():
        controller = servercontroller.ServerController()
        controller.start_server()


if __name__ == '__main__':
    #cimport OpenTTDStatsServer
    raise SystemExit(OpenTTDStatsServer.main())
