import aiohttp,random,requests
from src.libraries.GLOBAL_CONSTANT import API_KEY
apikey = API_KEY
alternate_apikey = [API_KEY]

def reset_apikey():
    global apikey
    apikey = API_KEY

async def getLocation():
    async with aiohttp.request('GET', 'http://wc.wahlap.net/maidx/rest/location') as resp:
        AddressData = await resp.json()
        return AddressData


def route_analysis(listinfo):
    nf = listinfo['segments']
    Msg = '首先冲到'
    for ddd in nf:
        for item in ddd.items():
            # print(item[0])
            if item[0] == 'bus':
                # print(item[1]['buslines'][0])
                try:
                    busname = item[1]['buslines'][0]['name']
                    start_action = item[1]['buslines'][0]['departure_stop']['name']
                    end_action = item[1]['buslines'][0]['arrival_stop']['name']
                    # print(start_action,end_action)
                    Msg += f'{start_action}坐{busname}到{end_action}\n再'
                except:
                    pass
                # print(item[1])
                # if 
    Msg += '应该就到了,你找找附近吧。'
    return Msg



async def GetGoShopData(address:str):
    global apikey
    params = {
    'key': apikey,
    'address':address
    }
    async with aiohttp.request('GET',f'https://restapi.amap.com/v3/geocode/geo',params=params) as resp:
        result = await resp.json()
        if result['infocode'] == "10044":
            apikey = random.choice(alternate_apikey)
            result = requests.get(f'https://restapi.amap.com/v3/geocode/geo',params={'key': apikey,'address':address}).json()
        return result['geocodes'][0]['location']
    


async def GetGoOutList(cityshops:list,latitude,longitude,city:str):
    GoShopList = []
    for address in cityshops:
        destination = await GetGoShopData(address['address'])
        params = {
            'key': apikey,
            'origin':f'{latitude},{longitude}',
            'destination': destination,
            'city':city
        }
        async with aiohttp.request('GET',f'https://restapi.amap.com/v3/direction/transit/integrated?',params=params) as resp:
            result = await resp.json()
            try:
                item = result['route']['transits'][0]
            except:
                GoShopList.append({'cost':'0','duration':0,'walking_distance':'0','name':'你脚下↓:'+address['mall'],'address':address['address'],'lacation':destination,'route_msg':''})
                continue
            try:
                route_msg = route_analysis(item)
            except:
                GoShopList.append({'cost':'0','duration':0,'walking_distance':'0','name':address['mall'],'address':address['address'],'lacation':destination,'route_msg':''})
                continue
            stime:int  = int(item['duration'])
            duration = (stime//60)+1 if stime%60 != 0 else stime//60
            # print({'cost':item['cost'],'duration':duration,'walking_distance':item['walking_distance'],'address':address['address']})
            GoShopList.append({'cost':item['cost'],'duration':duration,'walking_distance':item['walking_distance'],'name':address['mall'],'address':address['address'],'lacation':destination,'route_msg':route_msg})
    return GoShopList


async def GetCityShops(city:str,latitude,longitude):
    cityshops = []
    MaiMai_Location = await getLocation()
    for item in MaiMai_Location:
        if city in item['address']:
            cityshops.append(item)
    return await GetGoOutList(cityshops,latitude,longitude,city)


def MapCQ(name: str,Address: str,lat: str, lng: str):
    CqText = '[CQ:json,data={ "app": "com.tencent.map"&#44; "config": { "autosize": false&#44; "forward": true&#44; "type": "normal" }&#44; "desc": ""&#44; "meta": { "Location.Search": { "address": "'+ Address +'"&#44; "from": "plusPanel"&#44; "id": "10471098104178669718"&#44; "lat": "'+ lat +'"&#44; "lng": "'+ lng +'"&#44; "name": "'+ name +'" } }&#44; "prompt": "&#91;应用&#93;地图"&#44; "ver": "0.0.0.1"&#44; "view": "LocationShare" }]'
    return CqText

async def get_send_result(result):
    SendList = [{"type": "node","data": {"name": "Xray Bot","uin": "2468519813","content": [{"type": "text","data": {"text": "最快出勤点如下:"}}]}}]
    BY_SendList = [{"type": "node","data": {"name": "Xray Bot","uin": "2468519813","content": [{"type": "text","data": {"text": "最快出勤点如下:"}}]}}]
    
    for item in sorted(result, key = lambda i: i['duration'])[:5]:
        SendList.append({"type": "node","data": {"name": "Xray Bot","uin": "2468519813","content": [{"type": "text","data": {"text": f"地址:{item['name']}\n预计通勤时间:{item['duration']}分钟\n预计花费:{item['cost']}元\n{item['route_msg']}"}}]}})
        BY_SendList.append({"type": "node","data": {"name": "Xray Bot","uin": "2468519813","content": [{"type": "text","data": {"text": f"地址:{item['name']}\n预计通勤时间:{item['duration']}分钟\n预计花费:{item['cost']}元\n{item['route_msg']}"}}]}})
        SendList.append({"type": "node","data": {"name": "Xray Bot","uin": "2468519813","content": MapCQ(item['name'],item['address'],str(item['lacation']).split(',')[1],str(item['lacation']).split(',')[0])}})

    SendList.append({"type": "node","data": {"name": "Xray Bot","uin": "2468519813","content": [{"type": "text","data": {"text": "本功能由高达地图强力驱动,如有故障请联系机修。"}}]}})
    BY_SendList.append({"type": "node","data": {"name": "Xray Bot","uin": "2468519813","content": [{"type": "text","data": {"text": "本功能由高达地图强力驱动,如有故障请联系机修。"}}]}})
    return SendList,BY_SendList


async def getCityName(latitude,longitude):
    params = {
    'key': apikey,
    'location': f'{latitude},{longitude}',
    'radius': '1000',
    'extensions': 'all'
    }
    async with aiohttp.request('GET',f'https://restapi.amap.com/v3/geocode/regeo?',params=params) as resp:
        result = await resp.json()
        # params(result['regeocode']['addressComponent'])
        if result['regeocode']['addressComponent'].get('city',[]):
            return await GetCityShops(result['regeocode']['addressComponent']['city'],latitude,longitude)
        else:
            return await GetCityShops(result['regeocode']['addressComponent']['province'],latitude,longitude)