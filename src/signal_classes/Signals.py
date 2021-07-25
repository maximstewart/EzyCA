# Python imports
import threading, subprocess, os

# Gtk imports

# Application imports
from .mixins import *


def threaded(fn):
    def wrapper(*args, **kwargs):
        threading.Thread(target=fn, args=args, kwargs=kwargs).start()

    return wrapper


class Signals(Utils, CAGenerator, ServerCertGenerator):
    def __init__(self, settings):
        self.settings           = settings
        self.builder            = self.settings.returnBuilder()

        self.ca_entry_vbox      = self.builder.get_object("ca_entry_vbox")
        self.server_entry_vbox  = self.builder.get_object("server_entry_vbox")
        self.textview_buffer    = self.builder.get_object("textview_buffer")

        self.target_path        = None


    def set_work_directory(self, widget, data=None):
        self.target_path = widget.get_filename()


    def generate_ca_and_server_certs(self, widget):
        print("Generating CA and signed Server Certs...")
        ca_data          = []
        server_cert_data = []
        ca_entries       = self.ca_entry_vbox.get_children()
        server_entries   = self.server_entry_vbox.get_children()

        self.fill_data_block(ca_data, ca_entries)
        self.fill_data_block(server_cert_data, server_entries)

        buffer = self.textview_buffer
        domains = buffer.get_text(
                            buffer.get_start_iter(),
                            buffer.get_end_iter(),
                            True
                        ).strip().split("\n")

        assert(self.target_path != None and self.target_path != ''), "A target work directory must be set!"
        assert(len(ca_data) == len(ca_entries)), "All CA entries must be filled!"
        assert(len(server_cert_data) == (len(server_entries) - 2) ), "All Server Cert entries must be filled!"


        self.step_1_create_ca_settings(self.target_path, ca_data)
        self.step_2_create_signing_ca_settings(self.target_path, ca_data)
        self.step_3_create_openssl_server_cert_settings(self.target_path, server_cert_data, domains)
        self.step_4_generate_all(self.target_path)


    def step_4_generate_all(self, target_path):
        print("Step 4: Running generation process...")
        opensslcacnf                = target_path + "/openssl-ca-settings.cnf"
        opensslsigningcasettingscnf = target_path + "/openssl-signing-ca-settings.cnf"
        opensslservercnf            = target_path + "/openssl-server-cert.cnf"

        signedcertsdir              = target_path + "/signed_certs"
        cacertpem                   = target_path + "/cacert.pem"
        servercertpem               = target_path + "/servercert.pem"
        servercertcsr               = target_path + "/servercert.csr"
        indexfile                   = target_path + "/index.txt"
        serialfile                  = target_path + "/serial.txt"


        os.chdir(target_path)
        os.mkdir(signedcertsdir)
        with open(indexfile, 'a') as f:
            f.close()
        with open(serialfile, 'w') as f:
            f.write("01")

        print("\t\tCreating CA cert key...")
        # openssl req -batch -x509 -days 10000 -config ./openssl-ca.cnf -newkey
        #           rsa:4096 -sha256 -nodes -out cacert.pem -outform PEM
        command = ["openssl", "req", "-batch", "-x509", "-days", "10000", "-config", opensslcacnf, "-newkey", "rsa:4096",
                    "-sha256", "-nodes", "-out", cacertpem, "-outform", "PEM"]
        proc    = subprocess.Popen(command, stdout=subprocess.PIPE)
        proc.wait()
        # You can dump the certificate with the following.
        # openssl x509 -in cacert.pem -text -noout


        print("\t\tCreating Server cert key pare...")
        # openssl req -batch -config ./openssl-server.cnf -newkey rsa:2048
        #           -sha256 -nodes -out servercert.csr -outform PEM
        command = ["openssl", "req", "-batch", "-config", opensslservercnf, "-newkey", "rsa:4096", "-sha256", "-nodes",
                    "-out", servercertcsr, "-outform", "PEM"]
        proc    = subprocess.Popen(command, stdout=subprocess.PIPE)
        proc.wait()
        # You can inspect.
        # openssl req -text -noout -verify -in servercert.csr


        print("\t\tCertifying Server cert with our CA...")
        # openssl ca -batch -config ./openssl-ca.cnf -policy signing_policy
        #         -extensions signing_req -out servercert.pem -infiles servercert.csr
        command = ["openssl", "ca", "-batch", "-config", opensslsigningcasettingscnf,
                    "-policy", "signing_policy", "-extensions", "signing_req", "-out",
                    servercertpem, "-infiles", "servercert.csr"]
        proc    = subprocess.Popen(command, stdout=subprocess.PIPE)
        proc.wait()
        # Finally, you can inspect your freshly minted certificate with the following:
        # openssl x509 -in servercert.pem -text -noout



    def set_server_country(self, widget, data=None):
        self.builder.get_object("svrCountry").set_text(widget.get_text().strip())

    def set_server_state(self, widget, data=None):
        self.builder.get_object("svrState").set_text(widget.get_text().strip())

    def set_server_city(self, widget, data=None):
        self.builder.get_object("svrCity").set_text(widget.get_text().strip())

    def set_server_org(self, widget, data=None):
        self.builder.get_object("svrOrg").set_text(widget.get_text().strip())

    def set_server_email(self, widget, data=None):
        self.builder.get_object("svrEmail").set_text(widget.get_text().strip())
