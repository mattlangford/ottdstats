import sys
from . import servercontroller
from .config import Config
from .database.databasefactory import DatabaseFactory
import getopt

class OpenTTDStatsServer:

    @staticmethod
    def main(argv):
        startup = OpenTTDStatsServer.parse_arguments(argv)

        if startup['usage']:
            OpenTTDStatsServer.print_commandline_help()
            return
        if startup['upgrade'] or startup['create_config']:
            if startup['upgrade']:
                OpenTTDStatsServer.upgrade_or_create_db()
            if startup['create_config']:
                OpenTTDStatsServer.default_config(startup)
            return

        controller = servercontroller.ServerController(startup)
        controller.start_server()

    @staticmethod
    def parse_arguments(args):
        try:
            parsed_opts, parsed_args = getopt.getopt(args, "udhc:", ["config", "upgrade", 'help', 'config='])
        except getopt.GetoptError as ex:
            print((ex.msg))
            exit(1)

        startup = {
            'upgrade': False,
            'create_config': False,
            'usage': False,
            'config_path': ''
        }
        for opt, arg in parsed_opts:
            if opt in ('-u', '--upgrade'):
                startup['upgrade'] = True
            if opt in ('-d', '--write-default-config'):
                startup['create_config'] = True
            if opt in ('-h', '--help'):
                startup['usage'] = True
            if opt in ('-c', '--config'):
                startup['config_path'] = arg

        return startup

    @staticmethod
    def print_commandline_help():
        print("Usage: python server.py [options]")
        print("\n\t-h,--help \t\tprint this help and exit")
        print("\t-u,--upgrade\t\tupgrade database and exit")
        print("\t-d,--default-config\tWrite the default configuration file and exit")
        print("\t-c,--config\t\tSpecify the path for configuration")

    @staticmethod
    def default_config(startup):
        Config(startup['config_path'], True)

    @staticmethod
    def upgrade_or_create_db():
        config = Config()
        DatabaseFactory.createdatabase(config.database)

if __name__ == '__main__':
    #cimport OpenTTDStatsServer
    raise SystemExit(OpenTTDStatsServer.main(sys.argv[1:]))
