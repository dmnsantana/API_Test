import requests, json, subprocess, ssl, datetime, sys

from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import pandas as pd
from pandas.io.json import json_normalize


def to_excel_sheet(path, dataframe):
    print("Entro funcion excel")
    f = datetime.datetime.today().__str__()
    f = f.replace(":", "-")
    f = f.replace(".", "-")
    print(path + "/CN Maestro-" + f + ".xlsx")

    with pd.ExcelWriter("excels/CN Maestro-" + f + ".xlsx") as writer:
        dataframe.to_excel(writer, sheet_name="cnMaestro")

        print("Mensaje", "Excel creado con exito")


def JsonToCSV():
    return


def GetDataAPI(api_url, api_call_headers):
    temp_url = api_url
    offset = 0

    read = True
    df_total = pd.DataFrame()

    while read:

        api_url = api_url.format(str(offset))

        api_call_response = requests.get(api_url, headers=api_call_headers, verify=False)
        #print(api_url)

        a = json.loads(api_call_response.text)

        df = pd.json_normalize(a, record_path=['data'])

        offset = offset + 100

        # print(df.shape[0])

        df_total = pd.concat([df, df_total], axis=0)

        api_url = temp_url

        if df.shape[0] < 100:
            offset = offset + int(df.shape[0])
            read = False
        # print(offset)

    df_total = df_total.reset_index(drop=True)
    df_total = df_total[["ip", "name", "status", "network"]]
    return df_total


def API_CnMaestro(id, secret, serverAP, access_token_url):
    access_token_url = access_token_url.format(str(serverAP))

    client = BackendApplicationClient(client_id=id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url=access_token_url, client_id=id, client_secret=secret, verify=ssl.CERT_NONE)
    access_token = token['access_token']
    #print(access_token)

    api_call_headers = {'Authorization': 'Bearer ' + access_token}

    api_url_devices_offline = "https://prycnmap{}.claro.net.co/api/v2/devices?offset={}&status=offline&type=wifi-enterprise".format(
        str(serverAP), "{}")
    api_url_devices_online = "https://prycnmap{}.claro.net.co/api/v2/devices?offset={}&status=online&type=wifi-enterprise".format(
        str(serverAP), "{}")

    df_offline = GetDataAPI(api_url_devices_offline, api_call_headers)
    df_online = GetDataAPI(api_url_devices_online, api_call_headers)

    df_cnmaestro = pd.concat([df_offline, df_online], axis=0)

    return df_cnmaestro


if __name__ == "__main__":

    path = 'C:/Users/ec4975k/PycharmProjects/djangoProjects/pythonProject/API_Test'

    if not sys.warnoptions:
        import warnings

        warnings.simplefilter("ignore")

    id_ap1 = 'oTizXBG8MTa6gSgz'
    secret_ap1 = 'ISgtGUtabnKBMRA6RRLGpAMrNAFDXa'

    id_ap2 = "amx79B3FtBa70D4L"
    secret_ap2 = "b0UTB0KzT3YRn0xID8cCkdoreBD6H9"

    access_token_url = "https://prycnmap{}.claro.net.co/api/v2/access/token"

    df_server1 = API_CnMaestro(id_ap1, secret_ap1, 1, access_token_url)
    print("Termino aps 1")
    df_server2 = API_CnMaestro(id_ap2, secret_ap2, 2, access_token_url)
    print("Termino aps 2")
    df_cnmaestro = pd.concat([df_server1, df_server2], axis=0)

    print(df_cnmaestro)

    # path = path.replace(chr(92), '/')

    to_excel_sheet(path, df_cnmaestro)
