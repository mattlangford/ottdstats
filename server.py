if __name__ == '__main__':
    import OpenTTDStatsServer
    raise SystemExit(OpenTTDStatsServer.main())

import servercontroller

class OpenTTDStatsServer:
    pass

def main():
    controller = servercontroller.ServerController()
    controller.start_server()