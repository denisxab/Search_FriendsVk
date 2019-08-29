import time
import re
import concurrent.futures
import requests
import numpy

from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect # задает ссылку

from django.views import View



def instructions (request):
	return render(request,'webexamp/instructions.html')

def lesions (request):
	return render(request,'webexamp/lesions.html')

def git (request):
	return render(request,'webexamp/git.html')

def post_list(request):
	return render(request,'webexamp/index.html')



#https://www.youtube.com/watch?v=r7a3JNdkgy0

def vk_frend(request):
	return Vk_Frend(request).Main()


class Vk_Frend:
    """Vk_Frend"""

    def __init__(self, request):
        #super(Vk_Frend, self).__init__()

        start_time = time.time()
        self.request = request
        self.token = "f289aa40f289aa40f289aa4039f2e03297ff289f289aa40ae2c6b5129292562a1d4c02f"
        self.v = "5.74"

        self.user_id = self.test_id(request.POST['name_user'])

        if not self.user_id:
            self.Main()

        try:
            self.conts_frend = int(request.POST['similar'])
            if self.conts_frend >= 50:
                self.conts_frend = 50
        except ValueError:
            self.conts_frend = 2

        self.all_id, self.ol_id = [], []
        self.except_user = {'0': [], '1': []}

        self.skan()

        self.frend = self.resaut()  # Сравнение пользователей

        self.first_name = self.name(self.user_id)  # Имя обратившегося
        self.timesa = int(time.time() - start_time)



    def Main(self):

        if not self.user_id:
            return HttpResponse('ERROR ID')

        if not self.frend:
            return HttpResponse('У вас скрыты друзья либо нет общих друзей')

        return render(self.request, 'webexamp/vk_frend.html', context={
            'user_id': self.user_id,
            'conts_frend': self.conts_frend,
            'cont_frend': self.cont,
            'frend': self.frend,
            'Count': self.except_user['0'],
            'Hidden': self.except_user['1'],
            'first_name': self.first_name,
            'timesa': self.timesa,
        })

    def name(self, name_id):
        respons = requests.get('https://api.vk.com/method/users.get', params={
            'lang': 'ru',
            "access_token": self.token,
            'v': self.v,
            'user_id': name_id, }).json()
        return '{} {}'.format(respons['response'][0]['first_name'], respons['response'][0]['last_name'])

    def test_id(self, user_id):
        if not user_id:
            return False
        try:
            int(user_id)
            return user_id
        except ValueError:
            name = re.findall(re.compile(
                "\\w+(?![https://vk.com/id])+\\w"), user_id)[0]
            respons = requests.get('https://api.vk.com/method/utils.resolveScreenName', params={'lang': 'ru',
                                                                                                "access_token": self.token,
                                                                                                'v': self.v,'screen_name': name}).json()
            
            try:
                return respons['response']['object_id']
            except TypeError:
                return False

    def resaut(self):

        save_id = {}
        sav = []

        for x in self.all_id:
            for z in x[1]:
                if z in self.ol_id:
                    sav.append(z)

            if sav != [] and len(sav) >= self.conts_frend:
                save_id[x[0]] = sav
                sav = []


        i = {x[0]: len(x[1]) for x in save_id.items()}

        save_res = {x[0]: save_id[x[0]]
                    for x in sorted(i.items(), key=lambda x: x[1], reverse=True)}

        lst = [{'item1': t[0][1], 'item2': t[1], 'item3':t[0][0], 'item4':len(t[0][1])}
               for t in zip(save_res.items(), [self.name(x) for x in save_res])]  # Главный сборщик ответа

        return lst

    def skan_user(self, user_id):

        respons = requests.get('https://api.vk.com/method/friends.get', params={
            "access_token": self.token,
            'v': self.v,
            'user_id': user_id, }).json()
        try:
            if respons['response']['count'] <= 500:
                self.ol_id.append(user_id)
                self.all_id.append(numpy.array(
                    (user_id, tuple(respons['response']['items']))))

            else:
                self.except_user['0'].append(user_id)

        except KeyError:
            self.except_user['1'].append(user_id)

    def skan(self):

        respons = requests.get('https://api.vk.com/method/friends.get', params={
            "access_token": self.token,
            'v': self.v,
            'user_id': self.user_id, }).json()

        try:
            self.cont = int(respons['response']['count']) if respons['response']['count'] <= 350 else 350

            #13.2
            #list(map(self.skan_user, respons['response']['items'][:self.cont]))

            # 4.6
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                for x in executor.map(self.skan_user, respons['response']['items'][:self.cont]):
                    pass

            # 4.8
            # Dirty = []
            # Thre = [threading.Thread(target=self.skan_user,args=(x,)) for x in respons['response']['items'][:self.cont]]
            # for x in Thre:
            #     x.start()
            # for x in Thre:
            #     x.join()

            self.ol_id = numpy.array(self.ol_id)
            self.all_id = numpy.array(self.all_id)
            self.cont -= len(self.except_user['0'])+len(self.except_user['1'])

        except KeyError:
            pass
