# Python imports
import threading, subprocess, os

# Gtk imports

# Application imports


class CAGenerator:
    """Empty docstring for CAGenerator"""
    ca_settings = """# ----------------------------- NOTE
# Remember to disable very bottom when generating first ca key and pem.
# Check notes at [ CA_default ] section as well!
# ----------------------------- NOTE

HOME             = {}
RANDFILE         = $ENV::HOME/.rnd

####################################################################
[ ca ]
default_ca       = CA_default    # The default ca section

[ CA_default ]
default_days     = 3000          # How long to certify for
default_crl_days = 3000          # How long before next CRL
default_md       = sha256        # Use public key default MD
preserve         = no            # Keep passed DN ordering
x509_extensions  = ca_extensions # The extensions to add to the cert
email_in_dn      = no            # Don't concat the email in the DN
copy_extensions  = copy          # Required to copy SANs from CSR to cert

# ca_default_additional_block_marker

####################################################################
[ req ]
default_bits       = 4096
default_keyfile    = cakey.pem
distinguished_name = ca_distinguished_name
x509_extensions    = ca_extensions
string_mask        = utf8only


####################################################################
[ ca_distinguished_name ]
countryName                    = Country Name (2 letter code)
countryName_default            = {}
stateOrProvinceName            = State or Province Name (full name eg, 'North Carolina')
stateOrProvinceName_default    = {}
localityName                   = Locality/City Name (full name eg, 'Durham')
localityName_default           = {}
organizationName               = Organization Name (eg, company 'Microsoft')
organizationName_default       = {}
organizationalUnitName         = Organizational Unit (eg, division)
organizationalUnitName_default = {}
commonName                     = Common Name (e.g. server FQDN or YOUR name)
commonName_default             = {}
emailAddress                   = Email Address (eg, 'no-reply@microsoft.com')
emailAddress_default           = {}


####################################################################
[ ca_extensions ]
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid:always, issuer
basicConstraints       = critical, CA:true
keyUsage               = keyCertSign, cRLSign

# Extensions for a typical CA
# PKIX recommendation.
subjectKeyIdentifier    = hash
authorityKeyIdentifier  = keyid:always,issuer
basicConstraints        = critical,CA:true

# Key usage: This is typical for a CA certificate. However since it will prevent
# it being used as an test self-signed certificate it is best left out by default.
# keyUsage = cRLSign, keyCertSign

# Some might want this also...
# nsCertType = sslCA, emailCA

# subjectAltName=email:copy    # Include email address in subject alt name: another PKIX recommendation
# issuerAltName=issuer:copy    # Copy issuer details

# DER hex encoding of an extension: Beware experts only!
# obj=DER:02:03                                   # Where 'obj' is a standard or added object
# basicConstraints= critical, DER:30:03:01:01:FF  # You can even override a supported extension.


####################################################################
[ crl_ext ]
# CRL extensions. Only issuerAltName and authorityKeyIdentifier make any sense in a CRL.
# issuerAltName        = issuer:copy
authorityKeyIdentifier = keyid:always


####################################################################
[ proxy_cert_ext ]
# These extensions should be added when creating a proxy certificate
# This goes against PKIX guidelines but some CAs do it and some software
# requires this to avoid interpreting an end user certificate as a CA.
basicConstraints=CA:FALSE

# Here are some examples of the usage of nsCertType. If it is omitted
# the certificate can be used for anything *except* object signing.
# nsCertType = server                  # This is OK for an SSL server.
# nsCertType = objsign                 # For an object signing certificate this would be used.
# nsCertType = client, email           # For normal client using this is typical.
# nsCertType = client, email, objsign  # For everything including object signing.

# This is typical in keyUsage for a client certificate.
# keyUsage = nonRepudiation, digitalSignature, keyEncipherment

# This will be displayed in Netscape's comment listbox.
nsComment  = 'OpenSSL Generated Certificate'

# PKIX recommendations harmless if included in all certificates.
subjectKeyIdentifier=hash
authorityKeyIdentifier=keyid,issuer

# This stuff is for subjectAltName and issuerAltname.
# subjectAltName    = email:copy    # Import the email address.
# subjectAltName    = email:move    # An alternative to produce certificates that aren't deprecated according to PKIX.
# issuerAltName     = issuer:copy   # Copy subject details

#nsCaRevocationUrl  = http://www.domain.dom/ca-crl.pem
#nsBaseUrl
#nsRevocationUrl
#nsRenewalUrl
#nsCaPolicyUrl
#nsSslServerName

# This really needs to be in place for it to be a proxy certificate.
proxyCertInfo=critical,language:id-ppl-anyLanguage,pathlen:3,policy:foo


####################################################################
[ tsa ]
default_tsa = tsa_config1    # The default TSA section (Which is set below...)

[ tsa_config1 ]
# These are used by the TSA reply generation only.
dir		                = /etc/ssl		                # TSA root directory
serial		            = $dir/tsaserial	            # The current serial number
crypto_device	        = builtin		                # OpenSSL engine to use for signing
signer_cert	            = $dir/tsacert.pem 	            # The TSA signing certificate (optional)
certs		            = $dir/cacert.pem	            # Certificate chain to include in reply (optional)
signer_key	            = $dir/private/tsakey.pem       # The TSA private key (optional)
signer_digest           = sha256			            # Signing digest to use. (optional)
default_policy	        = tsa_policy1		            # Policy if request did not specify it (optional)
other_policies	        = tsa_policy2, tsa_policy3	    # Acceptable policies (optional)
digests                 = sha1, sha256, sha384, sha512  # Acceptable message digests
accuracy	            = secs:1, millisecs:500, microsecs:100	# (optional)
clock_precision_digits  = 0	                            # Number of digits after dot. (optional)
ordering		        = yes	                        # Is ordering defined for timestamps? (optional, default: no)
tsa_name		        = yes	                        # Must the TSA name be included in the reply? (optional, default: no)
ess_cert_id_chain	    = no	                        # Must the ESS cert id chain be included? (optional, default: no)
ess_cert_id_alg		    = sha1	                        # Algorithm to compute certificate identifier (optional, default: sha1)

# ca_signing_block_marker
"""

    ca_default_additional_block = """base_dir       = {}
certificate    = $base_dir/cacert.pem     # The CA certifcate
private_key    = $base_dir/cakey.pem      # The CA private key
new_certs_dir  = $base_dir/signed_certs/  # Location for new certs after signing
database       = $base_dir/index.txt      # Database index file
serial         = $base_dir/serial.txt     # The current serial number
unique_subject = no  # Set to 'no' to allow creation of several certificates with same subject.
"""

    ca_signing_block = """####################################################################
[ signing_policy ]
countryName            = optional
stateOrProvinceName    = optional
localityName           = optional
organizationName       = optional
organizationalUnitName = optional
commonName             = supplied
emailAddress           = optional

[ signing_req ]
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid,issuer
basicConstraints       = CA:FALSE
keyUsage               = digitalSignature, keyEncipherment
"""


    def step_1_create_ca_settings(self, path, data):
        print("Step 1: Creating CA Settings...")
        all_data   = [path] + data
        fpath      = path + "/openssl-ca-settings.cnf"
        output_str = self.ca_settings.format(*all_data)

        with open(fpath, "w") as f:
            f.write(output_str)


    def step_2_create_signing_ca_settings(self, path, data):
        print("Step 2: Creating Signing CA Settings...")
        all_data   = [path] + data
        fpath      = path + "/openssl-signing-ca-settings.cnf"
        output_str = self.ca_settings.format(*all_data)
        ca_block   = self.ca_default_additional_block.format(path)

        output_str = output_str.replace("# ca_default_additional_block_marker", ca_block)
        output_str = output_str.replace("# ca_signing_block_marker", self.ca_signing_block)

        with open(fpath, "w") as f:
            f.write(output_str)
