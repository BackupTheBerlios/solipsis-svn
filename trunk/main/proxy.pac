// configuration file PROXY.PAC 
// for Netscape Navigator 2.x (or more) and IE 4.x
//
// last modifications : Cf proxy.pac.journal
//
//=======================================================
//	FT networks list
//		192.140.0.0/16 a 192.145.0.0/16
//		193.248.0.0/16 a 193.249.0.0/16
//		193.251.128.0/16 a 193.251.255.0/16
//=======================================================


function FindProxyForURL(url, host)
{
	var hash = 0;
	if (isPlainHostName(host)) {
		return "DIRECT";
	}
	else if (isInNet(myIpAddress(), "10.160.170.0", "255.255.254.0")) {
		//Pb lenteur DIN
	return "PROXY 10.193.118.30:3128; PROXY 10.193.118.37:3128; DIRECT";
	}
	else if (isInNet(host, "127.0.0.1", "255.255.255.255")) {
		//localhost, no proxy.
                return "DIRECT";
	}
	else if (isInNet(host, "10.194.64.0", "255.255.255.0")) {
		// IP telephony network 
                return "DIRECT";
        }
	else if (isInNet(host, "10.194.74.0", "255.255.255.0")) {
		// mobisat network 
                return "DIRECT";
        }
	else if (isInNet(host, "10.194.90.0", "255.255.255.0")) {
		// IP MIB
		return "DIRECT";
        }
	else if (isInNet(host, "10.241.14.0", "255.255.255.224")) {
		//Project Centre de Contact IP
		return "DIRECT";
	}
	else if (host == "quickplace.ocisi.francetelecom.fr" ||
		host == "quickplace2.ocisi.francetelecom.fr") {
		// quickplace : LotusDomino 5.08 server
		return "DIRECT";
        }
	else if (isInNet(myIpAddress(), "10.193.0.0", "255.255.192.0") ||
         isInNet(myIpAddress(), "10.193.64.0", "255.255.224.0"))
        {
                // client is in LANNION
                // petrel, direct
                if (isInNet(host, "10.193.0.0", "255.255.192.0") ||
                    isInNet(host, "10.193.64.0", "255.255.224.0"))
                        return "DIRECT";
                else return "PROXY 10.193.21.179:3128; PROXY 10.42.12.23:3128; DIRECT";
        }
	else {
		if (isInNet(myIpAddress(), "139.100.0.0", "255.255.0.0") ||
			isInNet(myIpAddress(), "10.193.96.0", "255.255.224.0") ||
			isInNet(myIpAddress(), "10.193.128.0", "255.255.192.0") ||
			isInNet(myIpAddress(), "192.144.74.0", "255.255.255.0"))
		{
			//Le client is in ISSY.
                	if (isInNet(host, "10.193.96.0", "255.255.224.0") ||
	                    isInNet(host, "10.193.128.0", "255.255.192.0") || 
				isInNet(host, "139.100.0.0", "255.255.128.0") ||
				isInNet(host, "139.100.128.0", "255.255.248.0") ||
				isInNet(host, "139.100.136.0", "255.255.252.0") ||
				isInNet(host, "139.100.141.0", "255.255.255.0") ||
				isInNet(host, "139.100.142.0", "255.255.254.0") ||
				isInNet(host, "139.100.144.0", "255.255.240.0") ||
				isInNet(host, "139.100.160.0", "255.255.224.0") ||
				isInNet(host, "139.100.192.0", "255.255.192.0") ||
				isInNet(host, "192.144.74.0", "255.255.255.0"))
                        	return "DIRECT";
			//for domains *.fr *.net *.org -> p-goodway (10.193.118.30:3128)
			//for the rest 		-> niceway	(10.193.118.37:3128)
			else
			{
			hash = (host.length %2);
			if (hash == 0) 
				//we use P-GOODWAY - 10.193.118.30
        			return "PROXY 10.193.118.30:3128; PROXY 10.193.118.37:3128; DIRECT";
                                 //we use P-NICEWAY
                	else return "PROXY 10.193.118.37:3128;PROXY 10.193.118.30:3128; DIRECT";
			}
		}
		else if (isInNet(myIpAddress(), "10.193.192.0", "255.255.240.0"))
		{
			//client is in CAEN.
                	if (isInNet(host, "10.193.192.0", "255.255.240.0"))
				return "DIRECT";
 			else if (isInNet(host, "194.199.139.0", "255.255.255.0")) {
			//EPI network, domain cnet-caen, no proxy.
                		return "DIRECT";
        		}
 			else if (isInNet(host, "161.106.144.0", "255.255.255.0")) {
			//LATEMS network, for Alain VALLEE, no proxy.
                		return "DIRECT";
        		}
			else
			{
			hash = (host.length %2);
			if (hash == 0) 
			//we use c-proxy1  - 10.193.197.22
                        	return "PROXY 10.193.197.22:3128; PROXY 10.42.12.19:3128; DIRECT";
                        //we use c-proxy2  - 10.193.197.23
                        else return "PROXY 10.193.197.23:3128; PROXY 10.42.12.23:3128; DIRECT";
			}

                }
		else if (isInNet(myIpAddress(), "10.194.32.0", "255.255.224.0"))
		{
			//client is in RENNES.
                	if (isInNet(host, "10.194.32.0", "255.255.224.0"))
				return "DIRECT";
			else
			{
			hash = (host.length %2);
			if (hash == 0) 
			//we use r-proxy1  - 10.194.51.41
                        	return "PROXY 10.194.51.41:3128; PROXY 10.42.12.19:3128; DIRECT";
                        //we use r-proxy2  - 10.194.51.42
                        else return "PROXY 10.194.51.42:3128; PROXY 10.42.12.23:3128; DIRECT";
			}
		}
		else if (isInNet(myIpAddress(), "10.193.224.0", "255.255.240.0"))
		{
			//client is in SOPHIA.
			//we use s-proxy - 10.193.225.16
                        if (isInNet(host, "10.193.224.0", "255.255.240.0"))
                                return "DIRECT";
                        else return "PROXY 10.193.225.16:3128; PROXY 10.42.12.19:3128; DIRECT";

		}
		else if (isInNet(myIpAddress(), "10.194.0.0", "255.255.224.0"))
		{
			//client is in GRENOBLE.
                        if (isInNet(host, "10.194.0.0", "255.255.224.0"))
                                return "DIRECT";
			else
			{
			hash = (host.length %2);
			if (hash == 0) 
			//we use g-proxy1  - 10.194.29.10
                       	return "PROXY 10.194.29.10:3128; PROXY 10.42.12.19:3128; DIRECT";
                        //we use g-proxy2  - 10.194.29.11
                        else return "PROXY 10.194.29.11:3128; PROXY 10.42.12.23:3128; DIRECT";
			}
		}
		else if (isInNet(myIpAddress(), "10.193.208.0", "255.255.240.0"))
		{
			//client is in BELFORT.
			// we use b-proxy - 10.193.213.20
                        if (isInNet(host, "10.193.208.0", "255.255.240.0"))
                                return "DIRECT";
                        else return "PROXY 10.193.213.20:3128; PROXY 10.42.12.23:3128; DIRECT";
		}
		else if (isInNet(myIpAddress(), "10.193.240.0", "255.255.255.0")) {
			//client is in CEVENNES
			//we use GOODWAY - 10.42.12.19
                        if (isInNet(host, "10.193.240.0", "255.255.255.0"))
                                return "DIRECT";
			else return "PROXY 10.42.12.19:3128; PROXY 10.42.12.23:3128; DIRECT";
		}
		else if (isInNet(myIpAddress(), "10.193.241.0", "255.255.255.0") ||
			isInNet(myIpAddress(), "10.193.242.0", "255.255.255.0"))
		{
			//client is in CHISWICK (FTRD GB)
			//we use uk-proxy - 10.193.241.23
                	if (isInNet(host, "10.193.241.0", "255.255.255.0") ||
	                    isInNet(host, "10.193.242.0", "255.255.255.0"))
				return "DIRECT";
			else return "PROXY 10.193.241.19:3128; PROXY 10.42.12.23:3128; DIRECT";
		}
		else if (isInNet(myIpAddress(), "10.193.250.0", "255.255.254.0"))
		{
			//client is in BEIJING (FTRD CHINA)
			//we use ch-proxy - 10.193.250.16
                	if (isInNet(host, "10.193.250.0", "255.255.254.0"))
				return "DIRECT";
			else return "PROXY 10.193.250.16:3128; PROXY 10.42.12.19:3128; DIRECT";
		}
		else if (isInNet(myIpAddress(), "10.193.248.0", "255.255.255.0"))
		{
			//client is in BOSTON (FTRD US)
			//we use uk-proxy - 10.193.241.23
                	if (isInNet(host, "10.193.248.0", "255.255.255.0"))
				return "DIRECT";
			else if (shExpMatch(host, "arianet.bd.francetelecom.fr*"))
			// for arianet authentication problem with squid proxy
			// we use niceway as proxy
				return "PROXY 10.193.241.23:3128";
			else return "PROXY 10.193.248.130:3128; DIRECT";
		}
		else if (isInNet(myIpAddress(), "10.193.244.0", "255.255.254.0") ||
			isInNet(myIpAddress(), "10.193.246.0", "255.255.255.0") ||
			isInNet(myIpAddress(), "10.32.176.0", "255.255.255.0") ||
			isInNet(myIpAddress(), "10.33.176.0", "255.255.255.0"))
		{
			//client is in SF (FTRD US)
                	if (isInNet(host, "10.193.244.0", "255.255.254.0") ||
	                    isInNet(host, "10.193.246.0", "255.255.255.0") ||
			    isInNet(host, "10.32.176.0", "255.255.255.0") ||
			    isInNet(host, "10.33.176.0", "255.255.255.0"))
				return "DIRECT";
			else if (isInNet(myIpAddress(), "10.193.244.0", "255.255.255.0"))
			// Vlan 10.193.244
			//we use u-proxy1  - 10.193.244.46
                        	return "PROXY 10.193.244.46:3128; DIRECT";
			//
			// others Vlan of SF
                        //we use u-proxy2  - 10.193.244.47
                        else return "PROXY 10.193.244.247:3128; DIRECT";

		}
		// debut Alleray
                else if (isInNet(myIpAddress(), "10.158.4.0", "255.255.252.0"))
		{
			//client is in Alleray (FT)
			if (isInNet(host, "10.193.0.0", "255.255.0.0")  ||
	                    isInNet(host, "10.194.0.0", "255.255.0.0"))
			// for FTRD we use p-niceway or p-goodway as proxy server
                        return "PROXY 10.193.118.37:3128; PROXY 10.193.118.30:3128; DIRECT";				else //For FT hosts, we use proxy FT
                	if (isInNet(host, "10.0.0.0", "255.0.0.0")  ||
	                    isInNet(host, "193.248.0", "255.255.0.0"))
				return "PROXY proxy:8080 ; DIRECT";
			else
			// for Internet, we use p-niceway or p-goodway as proxy server
                        return "PROXY 10.193.118.37:3128; PROXY 10.193.118.30:3128; DIRECT";
		}
		// fin Alleray
else
 // we use p-goodway p-niceway for ADSL access
 return "PROXY 10.193.118.30:3128 ; PROXY 10.193.118.37:3128; DIRECT";
	}
}
