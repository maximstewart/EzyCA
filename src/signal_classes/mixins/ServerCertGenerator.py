# Python imports
import threading, subprocess, os

# Gtk imports

# Application imports


class ServerCertGenerator:
    """Empty docstring for ServerCertGenerator"""

    server_cert_settings = """# ----------------------------- NOTE
HOME                        = {}
RANDFILE                    = $ENV::HOME/.rnd


####################################################################
[ req ]
default_bits                = 2048
default_keyfile             = privkey.pem
distinguished_name          = server_distinguished_name
req_extensions              = server_req_extensions
string_mask                 = utf8only


####################################################################
[ server_distinguished_name ]
countryName                 = Country Name (2 letter code)
countryName_default         = {}
stateOrProvinceName         = State or Province Name (full name eg, 'North Carolina')
stateOrProvinceName_default = {}
localityName                = Locality/City Name (full name eg, 'Durham')
localityName_default        = {}
organizationName            = Organization Name (eg, company 'Microsoft')
organizationName_default    = {}
commonName                  = Common Name (e.g. server FQDN or YOUR name)
commonName_default          = {}
emailAddress                = Email Address (eg, 'no-reply@microsoft.com')
emailAddress_default        = {}


####################################################################
[ server_req_extensions ]
subjectKeyIdentifier         = hash
basicConstraints             = CA:FALSE
keyUsage                     = digitalSignature, keyEncipherment
subjectAltName               = @alternate_names
nsComment                    = "OpenSSL Generated Certificate"

####################################################################
[ alternate_names ]
# alternate_names_marker


# If you are developing and need to use your workstation as a server, then you may
# need to do the following for Chrome. Otherwise Chrome may complain a Common Name
# is invalid (ERR_CERT_COMMON_NAME_INVALID). I'm not sure what the relationship is
# between an IP address in the SAN and a CN in this instance.

# IPv4 localhost
IP.1     = 0.0.0.0
IP.2     = 127.0.0.1

# IPv6 localhost
IP.2     = ::1
"""


    def step_3_create_openssl_server_cert_settings(self, path, data, domains):
        print("Step 3: Creating OpenSSL Server Cert Settings...")
        all_data     = [path] + data
        fpath        = path + "/openssl-server-cert.cnf"
        output_str   = self.server_cert_settings.format(*all_data)
        domain_block = ""
        i            = 1

        for domain in domains:
            domain_block += "DNS.{}    = {}".format(*(i, domain + "\n"))
            i += 1

        output_str = output_str.replace("# alternate_names_marker", domain_block)
        with open(fpath, "w") as f:
            f.write(output_str)
