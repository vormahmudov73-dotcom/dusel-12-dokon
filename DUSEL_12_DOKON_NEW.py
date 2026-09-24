# DUSEL 12-DOKON — YANGI TOZA KOD
# Eski bot kodidan import qilinmaydi.
# DUSEL bo'limlari haqiqiy ichma-ich menyu sifatida yozilgan.
# Standard library + Telegram Bot API.

import os
import json
import time
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

BOT_TOKEN = os.getenv("BOT_TOKEN", "BU_YERGA_BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_PHONE = os.getenv("ADMIN_PHONE", "")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")
SHOP_LOCATION = os.getenv("SHOP_LOCATION", "")
PORT = int(os.getenv("PORT", "10000"))
API = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# ============================================================
# KATALOG MA'LUMOTLARI
# ============================================================

CATALOG = {'DUSEL': {'AKRIL-PANEL / ICHKI DUMALOQ AKRIL': [['AR10 10W', 1.1],
                                                 ['AR18 18W', 1.4],
                                                 ['AR24 24W', 2.1],
                                                 ['AR36 36W', 3.45],
                                                 ['AR48 48W', 6.0]],
           "AKRIL-PANEL / ICHKI TO'RTBURCHAK AKRIL": [['AS10 10W', 1.25],
                                                      ['AS18 18W', 1.5],
                                                      ['AS24 24W', 2.25],
                                                      ['AS36 36W', 3.6],
                                                      ['AS48 48W', 6.5]],
           'AKRIL-PANEL / TASHQI DUMALOQ AKRIL': [['ASR18 18W', 1.9],
                                                  ['ASR24 24W', 2.7],
                                                  ['ASR36 36W', 4.0],
                                                  ['ASR48 48W', 7.4]],
           "AKRIL-PANEL / TASHQI TO'RTBURCHAK AKRIL": [['ASS18 18W', 2.0],
                                                       ['ASS24 24W', 2.9],
                                                       ['ASS36 36W', 4.5],
                                                       ['ASS48 48W', 7.6]],
           'AKRIL-PANEL / AKRIL GALOGEN': [['UR6 6W krug', 1.6],
                                           ['UR12 12W krug', 2.2],
                                           ['UR24 24W krug', 3.3],
                                           ['UR36 36W krug', 4.8],
                                           ['US6 6W kvadrat', 1.7],
                                           ['US12 12W kvadrat', 2.4],
                                           ['US24 24W kvadrat', 3.6],
                                           ['US36 36W kvadrat', 5.0],
                                           ['DAXR 18W 6500K', 2.0],
                                           ['DAXR 24W 6500K', 2.9],
                                           ['DAXR 36W 6500K', 4.3]],
           'AKRIL-PANEL / ICHKI DUMALOQ PANEL': [['R6 6W', 1.1],
                                                 ['R9 9W', 1.45],
                                                 ['R12 12W', 1.7],
                                                 ['R15 15W', 2.1],
                                                 ['R18 18W', 2.3],
                                                 ['R24 24W', 3.8]],
           "AKRIL-PANEL / ICHKI TO'RTBURCHAK PANEL": [['S6 6W', 1.2],
                                                      ['S9 9W', 1.7],
                                                      ['S12 12W', 2.0],
                                                      ['S15 15W', 2.3],
                                                      ['S18 18W', 2.75],
                                                      ['S24 24W', 4.4]],
           'AKRIL-PANEL / TASHQI DUMALOQ PANEL': [['SR12 12W', 2.1], ['SR18 18W', 2.9], ['SR24 24W', 4.4]],
           "AKRIL-PANEL / TASHQI TO'RTBURCHAK": [['SS12 12W', 2.35], ['SS18 18W', 3.2], ['SS24 24W', 4.8]],
           'AKRIL-PANEL / PANEL 60ga60': [['S-48w', 6.5],
                                          ['S-60w', 7.0],
                                          ['S-72w', 7.5],
                                          ['SS48w naruj', 11.0],
                                          ['Art-72 6500K', 9.5],
                                          ['Art-96 6500K', 10.5],
                                          ['Ramka 60×60', 3.4]],
           'PRAJECKTOC-RKU / P1 MODEL': [['P1 10W', 1.8],
                                         ['P1 20W', 2.9],
                                         ['P1 30W', 4.5],
                                         ['P1 50W', 5.8],
                                         ['P1 100W', 10.5],
                                         ['P1 150W', 16.0],
                                         ['P1 200W', 21.0]],
           'PRAJECKTOC-RKU / P7 MODEL': [['P7 10W', 1.7],
                                         ['P7 20W', 2.6],
                                         ['P7 30W', 3.1],
                                         ['P7 50W', 4.7],
                                         ['P7 100W', 8.2],
                                         ['P7 150W', 13.3],
                                         ['P7 200W', 16.8]],
           'PRAJECKTOC-RKU / P6 MODEL': [['P6 50W', 6.5],
                                         ['P6 100W', 10.0],
                                         ['P6 200W', 18.0],
                                         ['P6 300W', 26.0],
                                         ['P6 400W', 33.0],
                                         ['P6 500W', 42.0],
                                         ['P6 600W', 63.0]],
           'PRAJECKTOC-RKU / P8 MODEL': [['P8 50W', 8.0],
                                         ['P8 100W', 14.0],
                                         ['P8 200W', 22.0],
                                         ['P8 300W', 32.0],
                                         ['P8 400W', 40.0],
                                         ['P8 500W', 52.0],
                                         ['P8 600W', 65.0],
                                         ['P8 800W', 93.0],
                                         ['P8 1000W', 125.0]],
           'PRAJECKTOC-RKU / PP MODEL': [['PP2 100W', 9.0],
                                         ['PP2 150W', 12.5],
                                         ['PP2 200W', 15.0],
                                         ['PP2 300W', 24.0],
                                         ['PP3 600W', 50.0],
                                         ['PP3 1000W', 65.0],
                                         ['PP3 2000W', 125.0],
                                         ['UFO LED 100W', 14.0],
                                         ['UFO 150W', 18.0],
                                         ['UFO 200W', 24.0]],
           'PRAJECKTOC-RKU / P9-RGB MODEL': [['RGBP 20W', 5.0],
                                             ['RGBP 30W', 7.0],
                                             ['RGBP 50W', 8.0],
                                             ['RGBP 100W', 17.0],
                                             ['P9-50 Green', 5.5],
                                             ['P9-100 Green', 9.0],
                                             ['P9-150 Green', 12.0],
                                             ['P9-200 Green', 14.0],
                                             ['P9-300 Green', 19.0],
                                             ['RGBP-50', 6.0],
                                             ['RGBP-100', 11.0],
                                             ['RGBP-150', 16.0],
                                             ['RGBP-200', 19.0],
                                             ['RGBP-300', 24.5],
                                             ['PD7-30 datchik', 6.5],
                                             ['PD7-50 datchik', 8.0]],
           'PRAJECKTOC-RKU / RKU-QUYOSH PANEL': [['RKU2-150W', 24.0],
                                                 ['RKU1-50W', 12.0],
                                                 ['RKU1-100W', 17.0],
                                                 ['RKU1-150W', 20.0],
                                                 ['RKU1-300W', 27.0],
                                                 ['RKU1-400W', 35.0],
                                                 ['Solar RKU3-100', 32.0],
                                                 ['Solar RKU3-200', 42.0],
                                                 ['Solar RKU3-300', 51.0],
                                                 ['Solar P1-200', 26.0],
                                                 ['Solar P1-300', 36.0],
                                                 ['Solar P1-400', 40.0],
                                                 ['Solar P2-100', 21.0],
                                                 ['Solar P2-150', 25.0],
                                                 ['Solar P2-200', 28.0],
                                                 ['Solar P2-400', 40.0]],
           'PRAJECKTOC-RKU / RKU-220V STALBA': [['RKU1-50W Yoritgich', 7.5],
                                                ['RKU2-50W Yoritgich', 19.0],
                                                ['RKU3-50W Yoritgich', 11.0],
                                                ['RKU3 100W Yoritgich', 17.0]],
           'PRAJECKTOC-RKU / FASAD PROJECTOR': [['FP1-30 12W 3000/2000K', 10.0],
                                                ['FP1-50 18W 3000/2000K', 12.0],
                                                ['FP1-100 36W 3000/2000K', 17.0],
                                                ['FP2-30 12W 2000K', 10.0],
                                                ['FP2-50 18W 2000K', 12.0],
                                                ['FP2-100 36W 2000K', 14.0],
                                                ['FP3-30 2000K', 8.0],
                                                ['FP3-30 4500K', 8.0],
                                                ['FP3-50 2000K', 10.0],
                                                ['FP3-50 4500K', 10.0],
                                                ['FP3-100 2000K', 14.0],
                                                ['FP3-100 4500K', 14.0],
                                                ['FP3-10 10W', 10.0],
                                                ['FP8-9 9W', 10.0],
                                                ['FP8-36 36W', 21.0]],
           'AKSESSUARLAR': [['Dusel Perehodnik Universal', 0.45],
                            ['Vilka DU-59', 0.25],
                            ['Vilka DU-60', 0.25],
                            ['Vilka DU-70', 0.25],
                            ['DU-69 Perenoska Vilka', 0.45],
                            ['Mesa sotka 3TALI DU-50', 0.8],
                            ['Carlos sotka 3TALI VKL DU-51', 1.15],
                            ['Pele sotka 3TALI S ZAZ DU-52', 15.0],
                            ['Sotka 4tali DU-56', 1.1],
                            ['Sotka 4tali vkl DU-57', 1.65],
                            ['Sotka 4tali USB DU-58', 3.0],
                            ['DUSEL 3m', 2.45],
                            ['DUSEL 5m', 3.35],
                            ['DUSEL 10m', 5.4],
                            ['Troynik ZAZM DU-67', 1.3],
                            ['Troynik BEZ ZAZ DU-68', 1.1],
                            ['Rozetka zashitnik', 0.12],
                            ['PREMIUM 2TALI-3M Udl', 2.8],
                            ['PREMIUM 2TALI -5M Udl', 3.7],
                            ['PREMIUM 2TALI -10M Udl', 6.4],
                            ['PREMIUM 3TALI -3M Udl', 2.9],
                            ['PREMIUM 3TALI -5M Udl', 3.9],
                            ['PREMIUM 3TALI -10M Udl', 7.0],
                            ['PREMIUM 4TALI -3M Udl', 3.2],
                            ['PREMIUM 4TALI -5M Udl', 4.5],
                            ['PREMIUM 4TALI -10M Udl', 8.0],
                            ['PREMIUM 5TALI -3M Udl', 3.5],
                            ['PREMIUM 5TALI -5M Udl', 4.7],
                            ['PREMIUM 5TALI -10M Udl', 8.5],
                            ['PREMIUM 2TALI -Kolodka', 1.0],
                            ['PREMIUM 3TALI -Kolodka', 1.1],
                            ['PREMIUM 4TALI -Kolodka', 1.3],
                            ['PREMIUM 5TALI -Kolodka', 1.4],
                            ['Perehodnik patron 01', 0.27],
                            ['Perehodnik patron 02', 0.32],
                            ['Perehodnik patron 03', 0.32],
                            ['Patron E27 White', 0.29],
                            ['Patron E27 Black', 0.29],
                            ['Patron E14 White', 0.25],
                            ['Patron E14 Black', 0.25],
                            ['Pultsv-1', 4.0],
                            ['Pult 01 (sekundsiz)', 4.2],
                            ['Pult 02 (sekundli)', 4.3],
                            ['Izolenta Black', 0.2],
                            ['Izolenta Blue', 0.2],
                            ['Izolenta White', 0.2],
                            ['Izolenta Green', 0.2],
                            ['Izolenta Yellow', 0.2],
                            ['Izolenta Red', 0.2]],
           'AKSESSUARLAR / DL-BI': [["DL-BI So'tka", 0.42],
                                    ['DL-BI 3M UDN', 1.1],
                                    ['DL-BI 5M UDN', 1.6],
                                    ['DL-BI 8M UDN', 2.2],
                                    ['DL-BI VILKA 2', 0.18],
                                    ['DL-BI VILKA 3', 0.18],
                                    ['DL-BI VILAK 4', 0.18]],
           'AKSESSUARLAR / DRAYVERLAR': [['Drayver 3W', 0.45],
                                         ['Drayver 8-24W', 0.55],
                                         ['Drayver 48W', 3.0],
                                         ['Akril Drayver 8-24W', 0.6],
                                         ['Akril Drayver 36-48W', 0.9],
                                         ['Neoclassic drayver 7-7W', 0.5],
                                         ['Neoclassic drayver 10+10W', 0.7],
                                         ['Xrustal Galogen orga', 0.6],
                                         ['Xrustal Drayver', 0.4],
                                         ['Kvadrat Galogen Drayver 7 15W', 0.55],
                                         ['Driver TS 6-9W', 0.45],
                                         ['Driver TS 15-18W', 0.45]],
           'GERMETIK / KALTSO': [['Germetik karobka dumaloq', 0.7],
                                 ['Germetik karobka to‘rtburchak katta', 0.65],
                                 ['Germetik karobka to‘rtburchak kichkina', 0.4],
                                 ['Kaltso Dumaloq', 0.065],
                                 ['Kaltso Dumaloq Gipsokarton', 0.11],
                                 ['Kaltso Dumaloq Katta', 0.075],
                                 ['Kaltso Dumaloq Qopqoqlik', 0.13],
                                 ['Kaltso Kvadrat', 0.28]],
           'SLIM NABOR': [['Slim nabor XC-2001 680W DUSEL', 110.0],
                          ['Slim nabor XC-2003 650W DUSEL', 120.0],
                          ['Slim nabor XC-2004 650W DUSEL', 120.0],
                          ['Slim nabor XC-2005 430W DUSEL', 75.0],
                          ['Slim nabor XC-2006 430W DUSEL', 75.0],
                          ['Slim nabor XC-2009 720W DUSEL', 100.0],
                          ['Slim nabor XC-2011 600W DUSEL', 110.0],
                          ['Slim nabor XC-2013 600W DUSEL', 110.0],
                          ['Slim nabor XC-2016 450W DUSEL', 90.0],
                          ['Slim nabor-16 120', 2.1],
                          ['Slim nabor-9 60', 1.4],
                          ['Slim nabor-7 40', 1.1],
                          ['90 gradus ugol', 0.6],
                          ['120 gradus ugol', 0.6],
                          ['Zvezda soidinitel', 0.6],
                          ['Pryamoy soidinitel', 0.6],
                          ['T soidinitel', 0.7],
                          ['X soidinitel', 0.7],
                          ['Soidinitel pitanya 220V', 0.6]],
           'MIRANDA': [['001 12W White', 4.0],
                       ['003 12W Black+Gold', 4.5],
                       ['003 12W Black+Black', 4.5],
                       ['003 24W White+Gold', 9.5],
                       ['003 24W Black+Gold', 9.5],
                       ['004 7W White', 5.0],
                       ['004 12W Black', 7.7],
                       ['004 12W White', 7.7],
                       ['005 12W Black', 4.7],
                       ['005 12W White', 4.7],
                       ['005 20W White', 6.0]],
           'STABILIZATOR / RELENIY': [['DRS95-500VA', 33.0],
                                      ['DRS95-1000VA', 37.0],
                                      ['DRS95-1500VA', 43.0],
                                      ['DRS95-2000VA', 50.0],
                                      ['DRS95-3000VA', 80.0],
                                      ['DRS95-5KVA', 120.0],
                                      ['DRS95-10KVA', 163.0],
                                      ['DRS95-12KVA', 177.0],
                                      ['DRS95-15KVA', 205.0],
                                      ['DRS95-20KVA', 240.0],
                                      ['DRS45-5KVA', 135.0],
                                      ['DRS45-10KVA', 181.0],
                                      ['DRS45-12KVA', 200.0],
                                      ['DRS45-15KVA', 242.0],
                                      ['DRS45-20KVA', 279.0],
                                      ['DRS45-30KVA', 511.0]],
           'STABILIZATOR / LATIRNIY': [['DSS-500VA', 48.0],
                                       ['DSS-1000VA', 60.0],
                                       ['DSS-1500VA', 63.0],
                                       ['DSS-2000VA', 84.0],
                                       ['DSS-5KVA', 154.0],
                                       ['DSS-10KVA', 211.0],
                                       ['DSS-15KVA', 302.0],
                                       ['DSS-20KVA', 465.0],
                                       ['DSS-30KVA', 630.0],
                                       ['DSS-50KVA', 1050.0]],
           'STABILIZATOR / KATTA STABLIZATOR': [['DSO-30KVA', 763.0],
                                                ['DSO-50KVA', 1350.0],
                                                ['DSO-60KVA', 1440.0],
                                                ['DTS-1KVA', 90.0],
                                                ['DTS-3KVA', 135.0],
                                                ['DTS-5KVA', 200.0],
                                                ['DTS-15KVA', 450.0],
                                                ['DTS-20KVA', 540.0],
                                                ['DTS-30KVA', 950.0]],
           'Dekorativ Rangli Patronlar': [['BRONZE', 1.8],
                                          ['SILVER', 1.8],
                                          ['COPPER', 1.8],
                                          ['BLACK', 1.8],
                                          ['CHOCO', 1.8]],
           'DUSEL GILLYANDA PATRON': [['Gilyanda patron 5×10 (50sm)', 5.0],
                                      ['Gilyanda patron 10×10 (1m)', 5.5],
                                      ['Gilyanda patron 10×20 (50sm)', 9.0],
                                      ['Gilyanda patron 15×30 (50sm)', 12.0],
                                      ['Gilyanda patron 20×20 (1m)', 11.0],
                                      ['Gilyanda patron 20×40 (50sm)', 18.0]],
           'SLIM LED T5 / T9 MODEL': [['T9-IR120 6500K', 4.7], ['T9-IR60 6500K', 3.2]],
           'SLIM LED T5 / T8 MODEL': [['T8-B60 18W', 6.3],
                                      ['T8-B90 24W', 7.2],
                                      ['T8-B120 36W', 8.0],
                                      ['T8-Comp 9W', 1.9],
                                      ['T8-Comp 18W', 2.3],
                                      ['T8 Derjatel 60sm', 0.6],
                                      ['T8 Derjatel 120sm', 0.9],
                                      ['T8 Derjatel 2×60sm', 0.9],
                                      ['T8 Derjatel 2×120sm', 1.0],
                                      ['T8 60 10W', 0.8],
                                      ['T8 120 20W', 1.1],
                                      ['T8 120 30W', 1.45],
                                      ['T8 120 50W', 1.7]],
           'SLIM LED T5 / SLIM MATVIY': [['Slim 20W 60sm', 2.0],
                                         ['Slim 30W 90sm', 2.5],
                                         ['Slim 40W 120sm', 2.8],
                                         ['Slim-30W 60sm', 2.8],
                                         ['Slim-40W 60sm', 3.0],
                                         ['Slim 50W 6500K 60sm', 4.0],
                                         ['Slim 60W 6500K 60sm', 4.1],
                                         ['Slim 80W 6500K 60sm', 4.4],
                                         ['Slim 60W Black', 4.1],
                                         ['Slim 80W Black', 4.4]],
           'SLIM LED T5 / T5 LAMPA': [['T5-AL 6W', 1.5], ['T5-AL 9W', 1.8], ['T5-AL 18W', 2.4]],
           'SLIM LED T5 / T5-PL': [['T5-PL 6W', 1.0], ['T5-PL 9W', 1.3], ['T5-PL 15W', 1.5], ['T5-PL 18W', 1.6]],
           'SLIM LED T5 / T5 LAMPA QUYVAT': [['T5-PL30 6W', 1.2],
                                             ['T5-PL60 9W', 1.4],
                                             ['T5-PL90 15W', 1.7],
                                             ['T5-PL120 18W', 1.9]],
           'SLIM LED T5 / T6 LAMPA': [['T6-PL30 6W', 0.9],
                                      ['T6-PL60 9W', 1.1],
                                      ['T6-PL90 15W', 1.4],
                                      ['T6-PL120 18W', 1.6]],
           'SLIM LED T5 / T8 ALYUMIN': [['T8-AL 9W', 2.0], ['T8-AL 18W', 2.8]],
           'SLIM LED T5 / GERMETIK SLIM LAMPALAR': [['Slim 40W IP65 Black', 4.8],
                                                    ['Slim 40W IP65', 4.8],
                                                    ['Slim 60W IP65 Black', 6.2]],
           'SLIM LED T5 / SLIM TRANSPARENT': [['Slim G60 60W', 5.0],
                                              ['Slim G80 60W', 5.3],
                                              ['Slim PS60 Black', 3.2],
                                              ['Slim PS80 Black', 4.1]],
           'AKRIL VA PANEL / PLAFONLAR — HI-TECH': [['BR8 8W', 1.6],
                                                    ['BR17 17W', 2.5],
                                                    ['BR23 23W', 3.8],
                                                    ['BS8 8W', 1.8],
                                                    ['BS17 17W', 2.9],
                                                    ['BS23 23W', 4.3],
                                                    ['YR9 9W 6500K', 1.9],
                                                    ['YR9 9W4000K', 1.9],
                                                    ['YR18 18W 6500K', 2.6],
                                                    ['YR18 18W 4000K', 2.6],
                                                    ['YR24 24W 6500K', 3.8],
                                                    ['YR24 24W 4000K', 3.8],
                                                    ['YR36 36W 6500K', 5.5],
                                                    ['YR36 36W 4000K', 5.5],
                                                    ['YNR 18 6500K', 2.8],
                                                    ['YNR 24 6500K', 4.1],
                                                    ['YNR 36 6500K', 5.8]],
           'AKRIL VA PANEL / AKRIL SENSOR PANEL': [['SASS 18w', 4.3],
                                                   ['SASS 24w', 5.2],
                                                   ['SASS 36w', 6.3],
                                                   ['SASR 18w', 4.2],
                                                   ['SASR 24w', 5.1],
                                                   ['SASR 36w', 6.2]],
           'AKRIL VA PANEL / SAUNA PLAFON': [['PR12 12W', 2.2],
                                             ['PR18 18W', 2.6],
                                             ['PR24 24W', 3.4],
                                             ['PS12 12W', 2.2],
                                             ['PS18 18W', 2.6],
                                             ['PS24 24W', 3.4],
                                             ['RPR18 18W', 2.5],
                                             ['RPR24 24W', 3.4],
                                             ['RPS18 18W', 2.5],
                                             ['RPS24 24W', 3.4]],
           'AKRIL VA PANEL / HI-TECH PLAFON': [['SP-30 White', 3.3], ['SP-40 White', 4.8], ['SP-40 Gold', 5.0]],
           'AKRIL VA PANEL / SENSOR PLAFON': [['DSS-12 12W', 5.7],
                                              ['DSS-18 18W', 6.4],
                                              ['DSS-24 24W', 8.5],
                                              ['DSR-12 12W', 5.2],
                                              ['DSR-18 18W', 5.7],
                                              ['DSR-24 24W', 8.0]],
           'IP 44 VILKA, ROZETKA': [['Dul15', 0.7],
                                    ['Dul16', 0.75],
                                    ['Dul17', 0.7],
                                    ['Dul18', 0.9],
                                    ['Dul21', 1.45],
                                    ['Dul11', 1.3],
                                    ['Dul19', 2.3],
                                    ['Dul20', 2.8],
                                    ['Dul12', 1.8],
                                    ['Dul13', 2.3],
                                    ['Dul14', 3.2],
                                    ['Dul22', 3.0]],
           'IP54 ROZETKA VKLUCHATEL': [['VKL 2 ROZ 1Du128', 2.6],
                                       ['VKL 1 ROZ 1DU127', 2.4],
                                       ['ROZ 2 DU126', 2.3],
                                       ['ROZ 1 DU125', 1.2],
                                       ['VKL 2 DU124', 1.4],
                                       ['VKL 1 DU123', 1.2]],
           'DUSEL DATCHIK': [['DD-01', 4.0],
                             ['DD-02', 4.3],
                             ['DD-03', 4.0],
                             ['DD-04 WHITE', 4.1],
                             ['DD-04 BLACK', 4.1],
                             ['DD-05', 4.1],
                             ['DD-06', 3.5],
                             ['FR-06', 1.5],
                             ['FR-10', 2.0],
                             ['FR-25', 2.9],
                             ['Sensor panel uchun datchik', 1.75]],
           'OFIS YORITGICHLARI': [['ZS1-9W 40sm 6500K Gold', 11.0]],
           'TREK YORITGICH RELS': [['TS1 20W Black 6500K', 2.4],
                                   ['TS1 30W Black 6500K', 3.0],
                                   ['TS1 40W Black 6500K', 4.4],
                                   ['TS1 20W Black 4500K', 2.4],
                                   ['TS1 30W Black 4500K', 3.0],
                                   ['TS1 40W Black 4500K', 4.4],
                                   ['TS1 20W White 6500K', 2.4],
                                   ['TS1 30W White 6500K', 3.0],
                                   ['TS1 40W White 6500K', 4.4],
                                   ['TS1 20W White 4500K', 2.4],
                                   ['TS1 30W White 4500K', 3.0],
                                   ['TS1 40W White 4500K', 4.4],
                                   ['TS2 20W Black 6500K', 3.3],
                                   ['TS2 30W Black 6500K', 4.5],
                                   ['TS2 40W Black 6500K', 7.0],
                                   ['TS2 20W Black 4500K', 3.3],
                                   ['TS2 30W Black 4500K', 4.5],
                                   ['TS2 40W Black 4500K', 7.0],
                                   ['TS2 20W White 6500K', 3.3],
                                   ['TS2 30W White 6500K', 4.5],
                                   ['TS2 40W White 6500K', 7.0],
                                   ['TS2 20W White 4500K', 3.3],
                                   ['TS2 30W White 4500K', 4.5],
                                   ['TS2 40W White 4500K', 7.0],
                                   ['TS3 30W Black 6500K', 5.8],
                                   ['TS4-40 Black M', 7.0],
                                   ['TS4-30 White M', 5.5],
                                   ['TS4-40 Black T', 7.5],
                                   ['TS4-30 White T', 6.0],
                                   ['Rels 1M Black', 1.3],
                                   ['Rels 1.5M Black', 1.9],
                                   ['Rels 2M Black', 2.6],
                                   ['Rels 3M Black', 3.9],
                                   ['Rels 1M WHITE', 1.3],
                                   ['Rels 1.5M WHITE', 1.9],
                                   ['Rels 2M WHITE', 2.6],
                                   ['Rels 3M WHITE', 3.9],
                                   ['Soedinitel Black', 0.4],
                                   ['Uglovoy soedinitel Black', 0.4],
                                   ['Krugliy soedinitel Black', 0.7],
                                   ['Avalniy soedinitel Black', 0.7],
                                   ['T soedinitel Black', 0.8],
                                   ['Soedinitel WHITE', 0.4],
                                   ['Uglovoy soedinitel WHITE', 0.4],
                                   ['Krugliy soedinitel WHITE', 0.7],
                                   ['Avalniy soedinitel WHITE', 0.7],
                                   ['T soedinitel WHITE', 0.8],
                                   ['Plyus soedinitel', 0.9]]},
 'SALID': {'SALID LIGEHT — SG': [['SG01-10 white', 5.0],
                                 ['SG01-10 black', 5.0],
                                 ['SG02-10 white', 3.2],
                                 ['SG02-10 black', 3.2],
                                 ['SG03-7 white', 5.0],
                                 ['SG03-7 black', 5.0],
                                 ['SG04-10 white', 5.7],
                                 ['SG04-10 black', 5.7],
                                 ['SG04-10/2 white', 11.0],
                                 ['SG04-10/2 black', 11.0],
                                 ['SG04-10/3 white', 17.0],
                                 ['SG04-10/3 black', 17.0],
                                 ['SG17-10 white', 5.3],
                                 ['SG17-10 black', 5.3],
                                 ['SG17-12 white', 5.0],
                                 ['SG17-12 black', 5.0],
                                 ['SG18-10 white', 5.3],
                                 ['SG18-10 black', 5.3],
                                 ['SG18-12 white', 5.0],
                                 ['SG18-12 black', 5.0],
                                 ['SG18-10/2 white', 10.5],
                                 ['SG18-10/2 black', 10.5],
                                 ['SG18-12/2 white', 10.0],
                                 ['SG18-10/3 white', 16.0],
                                 ['SG18-10/3 black', 16.0],
                                 ['SG18-12/3 white', 15.0],
                                 ['SG14-10 white+gold', 4.2],
                                 ['SG15-10 white+black', 4.2],
                                 ['SG16-10 white+black', 6.0],
                                 ['SG16-10/2 white+black', 11.0],
                                 ['SG16-12/2 white+black', 10.5],
                                 ['SG16-10/3 white+black', 16.0],
                                 ['SG16-12/3 white+black', 16.0],
                                 ['SG19-10 white', 3.8],
                                 ['SG19-10 black', 3.8],
                                 ['SG20-10 white', 2.8],
                                 ['SG20-10 black', 2.8],
                                 ['SG21-10 white', 5.0],
                                 ['SG21-10 black', 5.0],
                                 ['SG21-20 white', 8.0],
                                 ['SG21-20 black', 8.0],
                                 ['SG21-30 white', 11.5],
                                 ['SG21-30 black', 11.5],
                                 ['SG21-40 white', 16.0],
                                 ['SG21-40 black', 16.0],
                                 ['SG22-12 white', 7.0],
                                 ['SG22-12 black', 7.0],
                                 ['SG23-7 white', 4.3],
                                 ['SG23-7 black', 4.3],
                                 ['SG23-12 white', 4.7],
                                 ['SG23-12 black', 4.7],
                                 ['SG23-20 white', 8.5],
                                 ['SG23-20 black', 8.5],
                                 ['SG24-10 white', 5.7],
                                 ['SG24-10 black', 5.7],
                                 ['SG24-12 white', 5.7],
                                 ['SG24-12 black', 5.7],
                                 ['SG24-10/2 white', 10.5],
                                 ['SG24-10/2 black', 10.5],
                                 ['SG24-12/2 white', 10.0],
                                 ['SG24-12/2 black', 10.0],
                                 ['SG24-10/3 white', 16.0],
                                 ['SG24-10/3 black', 16.0],
                                 ['SG24-12/3 white', 15.0],
                                 ['SG25-12 white+ gold', 6.0],
                                 ['SG25-12 black+white', 6.0],
                                 ['SG25-12 black+chromium', 6.0],
                                 ['SG25-12*2 white+ gold', 12.0],
                                 ['SG25-12*2 black', 12.0],
                                 ['SG25-12*2 black+chromium', 12.0],
                                 ['SG27-15 WH', 7.0],
                                 ['SG27-15 BK+BC', 7.0],
                                 ['SG27-15 WH+K GD', 7.0],
                                 ['SG27-15 BK+K GD', 7.0],
                                 ['SG27-15*2 WH', 14.0],
                                 ['SG27-15*2 Bk+BC', 14.0],
                                 ['SG27-15*2 Wh +K GD', 14.0],
                                 ['SG27-15*2 Bk+K GD', 14.0],
                                 ['SG28-15*2 Wh+PL', 11.0],
                                 ['SG28-15*2 Bk+BC', 11.0],
                                 ['SG28-15*2 Wh+CH', 11.0],
                                 ['SG28-15*2 Wh+Rose GD', 11.0],
                                 ['SG29-15*2 WH', 11.0],
                                 ['SG29-15*2 BK', 11.0],
                                 ['SG29-15*2 GY', 11.0],
                                 ['SG29-15*2 WH+Rose GD', 11.0],
                                 ['SG29-15*2 Wh +PL', 11.0],
                                 ['SG29-15*2 Bk+Rose GD', 11.0],
                                 ['SG29-15*2 Bk +CH', 11.0],
                                 ['SG30-15 Wh +PL', 5.5],
                                 ['SG30-15 Gy+sl', 5.5],
                                 ['SG30-15*2 Wh +PL', 11.0],
                                 ['SG30-15*2 Gy+sl', 11.0],
                                 ['SG31-15 Wh', 10.0],
                                 ['SG31-15 Black', 10.0],
                                 ['SG32-12 White', 7.0],
                                 ['SG32-12 Bk +BC', 7.0],
                                 ['SG33-12 Wh+CH', 8.0],
                                 ['SG33-12 Bk +GD', 8.0],
                                 ['SG33-12*2 Wh+CH', 15.0],
                                 ['SG33-12*2 Bk +GD', 15.0],
                                 ['SG34-15 Gy', 7.0],
                                 ['SG35-18 WH', 8.0],
                                 ['SG35-18 BK', 8.0],
                                 ['SG35-18 WH+GY', 8.0],
                                 ['SG35-18 BK +GY', 8.0],
                                 ['SG35-24 WH', 9.0],
                                 ['SG35-24 BK', 9.0],
                                 ['SG35-24 WH+GY', 9.0],
                                 ['SG35-24 BK +GY', 9.0],
                                 ['SG36-12 WH', 5.5],
                                 ['SG36-12 BC+GY', 5.5]],
           'SALID LIGEHT — SN': [['SN01-15 silver', 5.0],
                                 ['SN01-15 black', 5.0],
                                 ['SN01-20 silver', 7.3],
                                 ['SN01-20 gold', 7.3],
                                 ['SN02-15 gold+silver', 5.7],
                                 ['SN02-15 chrome+silver', 5.7],
                                 ['SN02-15 gold+black', 5.7],
                                 ['SN02-20 gold+silver', 7.3],
                                 ['SN02-20 chrome+silver', 7.3],
                                 ['SN03-15 black+gold', 5.7],
                                 ['SN03-15 silver+gold', 5.7],
                                 ['SN03-15 chrome+silver', 5.7],
                                 ['SN03-20 chromium+gold', 7.3],
                                 ['SN04-15 silver+gold', 5.7],
                                 ['SN04-20 black+gold', 7.3],
                                 ['SN05-15 silver', 5.5],
                                 ['SN05-15 silver+gold', 5.5],
                                 ['SN05-15 chromium+gold', 5.5],
                                 ['SN05-15 black+gold', 5.5],
                                 ['SN05-20 silver+gold', 7.3],
                                 ['SN05-20 silver', 7.3],
                                 ['SN06-15 silver+gold', 5.7],
                                 ['SN06-15 black+gold', 5.7],
                                 ['SN07-15 chromium+chromium', 5.7],
                                 ['SN07-15 silver+gold', 5.7],
                                 ['SN08-15 gold+black', 5.7],
                                 ['SN08-15 black+silver', 5.7],
                                 ['SN08-15 black+gold', 5.7],
                                 ['SN08-15 chrome+silver', 5.7],
                                 ['SN08-15 chrome+gold', 5.7],
                                 ['SN08-20 chrome+gold', 7.3],
                                 ['SN09-15 chromium', 6.8],
                                 ['SN09-15 bronze', 6.8],
                                 ['SN10-15 black', 6.8],
                                 ['SN10-15 silver', 6.8],
                                 ['SN10-15 gold', 6.8],
                                 ['SN10-15 chromium', 6.8],
                                 ['SN11-15 bronze', 5.6],
                                 ['SN12-15 black', 5.5],
                                 ['SN13-15 silver', 5.5],
                                 ['SN14-20 chromium', 7.3]]}}

# Yuqori menyuda faqat mana shu guruhlar chiqadi.
# Ichki bo'limlar tashqarida TAKRORLANMAYDI.
DUSEL_GROUPS = {'AKRIL VA PANEL': ['AKRIL-PANEL / ICHKI DUMALOQ AKRIL',
                    "AKRIL-PANEL / ICHKI TO'RTBURCHAK AKRIL",
                    'AKRIL-PANEL / TASHQI DUMALOQ AKRIL',
                    "AKRIL-PANEL / TASHQI TO'RTBURCHAK AKRIL",
                    'AKRIL-PANEL / AKRIL GALOGEN',
                    'AKRIL-PANEL / ICHKI DUMALOQ PANEL',
                    "AKRIL-PANEL / ICHKI TO'RTBURCHAK PANEL",
                    'AKRIL-PANEL / TASHQI DUMALOQ PANEL',
                    "AKRIL-PANEL / TASHQI TO'RTBURCHAK",
                    'AKRIL-PANEL / PANEL 60ga60',
                    'AKRIL VA PANEL / PLAFONLAR — HI-TECH',
                    'AKRIL VA PANEL / AKRIL SENSOR PANEL',
                    'AKRIL VA PANEL / SAUNA PLAFON',
                    'AKRIL VA PANEL / HI-TECH PLAFON',
                    'AKRIL VA PANEL / SENSOR PLAFON'],
 'PROYEKTORLAR': ['PRAJECKTOC-RKU / P1 MODEL',
                  'PRAJECKTOC-RKU / P7 MODEL',
                  'PRAJECKTOC-RKU / P6 MODEL',
                  'PRAJECKTOC-RKU / P8 MODEL',
                  'PRAJECKTOC-RKU / PP MODEL',
                  'PRAJECKTOC-RKU / P9-RGB MODEL',
                  'PRAJECKTOC-RKU / RKU-QUYOSH PANEL',
                  'PRAJECKTOC-RKU / RKU-220V STALBA',
                  'PRAJECKTOC-RKU / FASAD PROJECTOR'],
 'AKSESSUARLAR': ['AKSESSUARLAR', 'AKSESSUARLAR / DL-BI', 'AKSESSUARLAR / DRAYVERLAR'],
 'SLIM LED': ['SLIM LED T5 / T9 MODEL',
              'SLIM LED T5 / T8 MODEL',
              'SLIM LED T5 / SLIM MATVIY',
              'SLIM LED T5 / T5 LAMPA',
              'SLIM LED T5 / T5-PL',
              'SLIM LED T5 / T5 LAMPA QUYVAT',
              'SLIM LED T5 / T6 LAMPA',
              'SLIM LED T5 / T8 ALYUMIN',
              'SLIM LED T5 / GERMETIK SLIM LAMPALAR',
              'SLIM LED T5 / SLIM TRANSPARENT']}
DUSEL_OTHER = ['GERMETIK / KALTSO',
 'SLIM NABOR',
 'MIRANDA',
 'STABILIZATOR / RELENIY',
 'STABILIZATOR / LATIRNIY',
 'STABILIZATOR / KATTA STABLIZATOR',
 'Dekorativ Rangli Patronlar',
 'DUSEL GILLYANDA PATRON',
 'IP 44 VILKA, ROZETKA',
 'IP54 ROZETKA VKLUCHATEL',
 'DUSEL DATCHIK',
 'OFIS YORITGICHLARI',
 'TREK YORITGICH RELS']

SECTION_IDS = {}
PRODUCT_IDS = {}

def rebuild_ids():
    SECTION_IDS.clear()
    PRODUCT_IDS.clear()
    sid = 1
    pid = 1
    for brand, sections in CATALOG.items():
        for section, items in sections.items():
            SECTION_IDS[(brand, section)] = sid
            sid += 1
            for idx, _ in enumerate(items):
                PRODUCT_IDS[(brand, section, idx)] = pid
                pid += 1

rebuild_ids()

# ============================================================
# TELEGRAM API
# ============================================================

def api(method, data=None):
    if BOT_TOKEN == "BU_YERGA_BOT_TOKEN":
        print("BOT_TOKEN sozlanmagan")
        return None
    try:
        body = None
        headers = {}
        if data is not None:
            body = urllib.parse.urlencode(data).encode("utf-8")
            headers["Content-Type"] = "application/x-www-form-urlencoded"
        req = urllib.request.Request(API + method, data=body, headers=headers)
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        print("API xato:", e)
        return None

def send(chat_id, text, keyboard=None):
    data = {"chat_id": str(chat_id), "text": text, "parse_mode": "HTML"}
    if keyboard is not None:
        data["reply_markup"] = json.dumps(keyboard, ensure_ascii=False)
    return api("sendMessage", data)

def answer_callback(callback_id):
    api("answerCallbackQuery", {"callback_query_id": callback_id})

def kb(rows):
    return {"inline_keyboard": [[{"text": text, "callback_data": data}] for text, data in rows]}

# ============================================================
# RENDER HEALTH
# ============================================================

class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"DUSEL 12-DOKON NEW BOT OK")
    def log_message(self, *args):
        pass

def start_health():
    ThreadingHTTPServer(("0.0.0.0", PORT), Health).serve_forever()

# ============================================================
# MENYULAR
# ============================================================

def main_menu():
    return kb([
        ("🛍 Mahsulotlar", "brands"),
        ("🔎 Qidirish", "search"),
        ("🛒 Savat", "cart"),
        ("📍 Lokatsiya", "location"),
        ("📞 Admin bilan bog'lanish", "contact"),
        ("📩 Takliflar", "suggest")
    ])

def show_brands(chat_id):
    rows = []
    for brand, sections in CATALOG.items():
        if sections:
            rows.append(("🏷 " + brand, "brand:" + brand))
    rows.append(("⬅️ Asosiy menyu", "home"))
    send(chat_id, "🏷 <b>Brendni tanlang:</b>", kb(rows))

def show_dusel_sections(chat_id):
    rows = []
    # Faqat 4 ta asosiy guruh.
    for index, group in enumerate(DUSEL_GROUPS):
        rows.append(("📁 " + group, "group:" + str(index)))
    # Guruhga kirmaydigan bo'limlar.
    for section in DUSEL_OTHER:
        sid = SECTION_IDS[("DUSEL", section)]
        rows.append(("📂 " + section, "sec:" + str(sid)))
    rows.append(("⬅️ Brendlar", "brands"))
    send(chat_id, "🏷 <b>DUSEL</b>\n\n📂 <b>Bo'limni tanlang:</b>", kb(rows))

def show_group(chat_id, group_index):
    names = list(DUSEL_GROUPS)
    if group_index < 0 or group_index >= len(names):
        return
    group = names[group_index]
    rows = []
    for section in DUSEL_GROUPS[group]:
        sid = SECTION_IDS[("DUSEL", section)]
        if " / " in section:
            label = section.split(" / ", 1)[1]
        else:
            label = section
        if section.startswith("AKRIL-PANEL / "):
            label = "AKRIL-PANEL — " + section.split(" / ", 1)[1]
        elif section.startswith("AKRIL VA PANEL / "):
            label = "AKRIL LED PANEL — " + section.split(" / ", 1)[1]
        rows.append(("📂 " + label, "sec:" + str(sid)))
    rows.append(("⬅️ DUSEL", "brand:DUSEL"))
    send(chat_id, "📁 <b>" + group + "</b>\n\nIchki bo'limni tanlang:", kb(rows))

def show_section(chat_id, brand, section):
    items = CATALOG.get(brand, {}).get(section)
    if items is None:
        send(chat_id, "❌ Bo'lim topilmadi.")
        return
    rows = []
    for idx, (product, price) in enumerate(items):
        rows.append((f"📦 {product} — ${price:g}", f"prd:{PRODUCT_IDS[(brand, section, idx)]}"))
    rows.append(("⬅️ Orqaga", "brand:" + brand))
    send(chat_id, f"📂 <b>{section}</b>\n\nMahsulotni tanlang:", kb(rows))

# ============================================================
# ID RESOLVERLAR
# ============================================================

def section_by_id(sid):
    for key, value in SECTION_IDS.items():
        if value == sid:
            return key
    return None

def product_by_id(pid):
    for key, value in PRODUCT_IDS.items():
        if value == pid:
            return key
    return None

# ============================================================
# SAVAT
# ============================================================

CARTS = {}

def cart_text(chat_id):
    cart = CARTS.get(chat_id, [])
    if not cart:
        return "🛒 <b>Savat bo'sh.</b>"
    total = sum(x[3] * x[4] for x in cart)
    lines = ["🛒 <b>Savat:</b>"]
    for i, (brand, section, product, price, qty) in enumerate(cart, 1):
        lines.append(f"{i}. {product} — ${price:g} × {qty} = <b>${price*qty:g}</b>")
    lines.append(f"\n💵 Jami: <b>${total:g}</b>")
    return "\n".join(lines)

def show_cart(chat_id):
    send(chat_id, cart_text(chat_id), kb([
        ("🗑 Savatni tozalash", "cartclear"),
        ("📤 Buyurtma yuborish", "order"),
        ("⬅️ Asosiy menyu", "home")
    ]))

# ============================================================
# QIDIRUV
# ============================================================

SEARCH_STATE = {}

def search_prompt(chat_id):
    SEARCH_STATE[chat_id] = True
    send(chat_id, "🔎 <b>Mahsulot qidirish</b>\n\nMahsulot nomi yoki kodini yozing:", kb([("⬅️ Bekor qilish", "home")]))

def search_products(chat_id, query):
    q = query.strip().casefold()
    if len(q) < 2:
        send(chat_id, "❌ Kamida 2 ta belgi kiriting.")
        return
    results = []
    for brand, sections in CATALOG.items():
        for section, items in sections.items():
            for idx, (product, price) in enumerate(items):
                hay = f"{product} {section} {brand}".casefold()
                if q in hay:
                    results.append((brand, section, idx, product, price))
    if not results:
        send(chat_id, "🔎 <b>Natija topilmadi.</b>\n\nBoshqa nom yoki kod bilan urinib ko'ring.", kb([
            ("🔎 Yana qidirish", "search"),
            ("⬅️ Asosiy menyu", "home")
        ]))
        return
    rows = []
    for brand, section, idx, product, price in results[:50]:
        pid = PRODUCT_IDS[(brand, section, idx)]
        rows.append((f"📦 {product} — ${price:g}", f"prd:{pid}"))
    rows.append(("🔎 Yana qidirish", "search"))
    rows.append(("⬅️ Asosiy menyu", "home"))
    send(chat_id, f"🔎 <b>{len(results)} ta natija topildi.</b>", kb(rows))

# ============================================================
# CALLBACK
# ============================================================

def callback(update):
    q = update.get("callback_query") or {}
    cid = q.get("id")
    msg = q.get("message") or {}
    chat_id = (msg.get("chat") or {}).get("id")
    data = q.get("data", "")
    answer_callback(cid)
    if not chat_id:
        return

    if data == "home":
        SEARCH_STATE.pop(chat_id, None)
        send(chat_id, "🏠 <b>Asosiy menyu</b>", main_menu())
        return
    if data == "brands":
        SEARCH_STATE.pop(chat_id, None)
        show_brands(chat_id)
        return
    if data == "search":
        search_prompt(chat_id)
        return
    if data == "cart":
        show_cart(chat_id)
        return
    if data == "cartclear":
        CARTS[chat_id] = []
        show_cart(chat_id)
        return
    if data == "location":
        send(chat_id, "📍 <b>12-DOKON lokatsiyasi</b>\n\n" + (SHOP_LOCATION or "Lokatsiya hali sozlanmagan."), main_menu())
        return
    if data == "contact":
        text = "📞 <b>Admin bilan bog'lanish</b>"
        if ADMIN_USERNAME:
            text += "\nTelegram: " + ADMIN_USERNAME
        if ADMIN_PHONE:
            text += "\nTelefon: " + ADMIN_PHONE
        send(chat_id, text, main_menu())
        return
    if data == "suggest":
        send(chat_id, "📩 Taklifingizni shu chatga yozib yuboring. Admin ko'rib chiqadi.", main_menu())
        return
    if data.startswith("brand:"):
        brand = data[6:]
        if brand == "DUSEL":
            show_dusel_sections(chat_id)
        elif brand in CATALOG:
            rows = []
            for section in CATALOG[brand]:
                sid = SECTION_IDS[(brand, section)]
                label = section.replace("SALID LIGEHT — ", "")
                rows.append(("📂 " + label, "sec:" + str(sid)))
            rows.append(("⬅️ Brendlar", "brands"))
            send(chat_id, f"🏷 <b>{brand}</b>\n\nBo'limni tanlang:", kb(rows))
        return
    if data.startswith("group:"):
        show_group(chat_id, int(data[6:]))
        return
    if data.startswith("sec:"):
        item = section_by_id(int(data[4:]))
        if item:
            show_section(chat_id, *item)
        return
    if data.startswith("prd:"):
        item = product_by_id(int(data[4:]))
        if not item:
            return
        brand, section, idx = item
        product, price = CATALOG[brand][section][idx]
        CARTS.setdefault(chat_id, []).append((brand, section, product, price, 1))
        send(chat_id, f"📦 <b>{product}</b>\n💵 Narxi: <b>${price:g}</b>\n\n✅ Savatga qo'shildi.", kb([
            ("🛒 Savatni ko'rish", "cart"),
            ("⬅️ Bo'limga qaytish", "sec:" + str(SECTION_IDS[(brand, section)])),
            ("🏠 Asosiy menyu", "home")
        ]))
        return
    if data == "order":
        cart = CARTS.get(chat_id, [])
        if not cart:
            send(chat_id, "🛒 Savat bo'sh.")
            return
        text = "📦 <b>YANGI BUYURTMA</b>\n\n" + cart_text(chat_id)
        if ADMIN_ID:
            send(ADMIN_ID, text)
        send(chat_id, "✅ Buyurtma adminga yuborildi.", main_menu())
        CARTS[chat_id] = []

# ============================================================
# XABARLAR
# ============================================================

def message(update):
    m = update.get("message") or {}
    chat_id = (m.get("chat") or {}).get("id")
    if not chat_id:
        return
    text = (m.get("text") or "").strip()
    if text == "/start":
        SEARCH_STATE.pop(chat_id, None)
        send(chat_id, "🏠 <b>DUSEL 12-DOKON</b>\n\nKerakli bo'limni tanlang:", main_menu())
        return
    if SEARCH_STATE.get(chat_id) and text:
        SEARCH_STATE.pop(chat_id, None)
        search_products(chat_id, text)
        return
    if text == "🛍 Mahsulotlar":
        show_brands(chat_id)
    elif text == "🔎 Qidirish":
        search_prompt(chat_id)
    elif text == "🛒 Savat":
        show_cart(chat_id)
    elif text == "📍 Lokatsiya":
        send(chat_id, SHOP_LOCATION or "📍 Lokatsiya hali sozlanmagan.", main_menu())
    elif text == "📞 Admin bilan bog'lanish":
        send(chat_id, "📞 " + (ADMIN_USERNAME or "") + "\n" + (ADMIN_PHONE or ""), main_menu())
    elif text == "📩 Takliflar":
        send(chat_id, "📩 Taklifingizni shu chatga yozing.", main_menu())

# ============================================================
# POLLING
# ============================================================

def run():
    if BOT_TOKEN == "BU_YERGA_BOT_TOKEN":
        raise SystemExit("BOT_TOKEN ni Render Environment Variables ga kiriting.")
    threading.Thread(target=start_health, daemon=True).start()
    offset = None
    print("DUSEL 12-DOKON NEW BOT ISHGA TUSHDI")
    while True:
        try:
            data = {"timeout": "50", "allowed_updates": json.dumps(["message", "callback_query"])}
            if offset is not None:
                data["offset"] = str(offset)
            result = api("getUpdates", data)
            if not result or not result.get("ok"):
                time.sleep(5)
                continue
            for update in result.get("result", []):
                offset = update["update_id"] + 1
                if update.get("callback_query"):
                    callback(update)
                elif update.get("message"):
                    message(update)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print("RUN xato:", e)
            time.sleep(5)

if __name__ == "__main__":
    run()
