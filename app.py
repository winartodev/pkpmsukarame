from flask import Flask, render_template, request, flash
from markupsafe import Markup
import requests, json

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# api
covid_API = "https://data.covid19.go.id/public/api/"
rs_API = "https://rs-bed-covid-api.vercel.app/api/"

def dataFilter(nama_provinsi, data):
    result = list(filter(lambda provinsi: provinsi["key"] == nama_provinsi,  data["list_data"]))[0]
    return result

def getDataCovid():
    # indonesia API
    indonesia = covid_API + "update.json"
    indonesia = json.loads(requests.get(indonesia).text)

    # lampung API
    lampung = covid_API + "prov.json"
    lampung = json.loads(requests.get(lampung).text)
    
    data_covid = {
        "tanggal": lampung["last_date"],
        "indonesia":{
            'data':indonesia["data"], 
            "penambahan":indonesia["update"]["penambahan"], 
            "total":indonesia["update"]["total"]
            },
        "provinsi": {
            "lampung": dataFilter("LAMPUNG", lampung)
        }
    }

    return data_covid

def getCities():
    cityResponse = rs_API + "get-cities?provinceid=18prop"
    cities = json.loads(requests.get(cityResponse).text)
    return cities

# dapetin rumahsakit berdasarkan kota dan type apakah untuk covid dan non-covid
def getHospitals(cityId=None, type=None):
    hospitalResponse = rs_API + "get-hospitals?provinceid=18prop&cityid="+cityId+"&type="+type+""
    hospitals = json.loads(requests.get(hospitalResponse).text)
    # print(hospitals)
    return hospitals

dataCovid = getDataCovid()
dataCities = getCities()

@app.route("/")
def index():
    return render_template('index.html', result=dataCovid, cities=dataCities, hospitals=None)

@app.route("/rumahsakit", methods=["GET", "POST"])
def showHospitals():
    if request.method == 'POST':
        cityId = request.form['city']
        tempatTidur = request.form['tempatTidur']

        hostpitals = getHospitals(str(cityId), str(tempatTidur))
        # print(hostpitals)
        cityName = list(filter(lambda city: city["id"] == cityId, dataCities['cities']))[0]

        message = Markup("<span class=""fw-bold"">"+str(cityName['name'])+"</span>"+" ditemukan <span class=""fw-bold"">" + str(len(hostpitals['hospitals'])) + "</span> Rumah Sakit")
        flash(message)
        return render_template('index.html', result=dataCovid, cities=dataCities, hospitals=hostpitals, bedType=tempatTidur)
    else:
        return render_template('index.html', result=dataCovid, cities=dataCities, hospitals=None)

@app.route("/rumahsakit/<bedtype>/<id_rumahsakit>", methods=["GET", "POST"])
def hospitalInfo(bedtype, id_rumahsakit):
    getBedDetail = rs_API + "/get-bed-detail?hospitalid="+id_rumahsakit+"&type="+bedtype+""
    bedDetailRespondse = json.loads(requests.get(getBedDetail).text)
    # return render_template('rs-detail.html', id=id_rumahsakit)
    return bedDetailRespondse

if __name__ == "__main__":
    app.run()
