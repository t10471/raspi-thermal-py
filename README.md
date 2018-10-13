# raspi-thermal-py

Conta™ サーモグラフィー AMG8833搭載とAdafruit-AMG88xxライブラリをつかってRemoのエアコンを操作する
Raspberry Piのアプリケーション



<table>
<tr>
<th>
<img src="https://camo.qiitausercontent.com/9d6584fe7959e50c58fbe00bbc39fc69ff338a99/68747470733a2f2f71696974612d696d6167652d73746f72652e73332e616d617a6f6e6177732e636f6d2f302f373132332f63373536303965632d313638652d316464652d396266352d6431653963386563316661312e706e67" height="200"/>
</th>
<th>
<img src="https://camo.qiitausercontent.com/54ea0de335c452a2d4a1a56e75807f9a67d33a51/68747470733a2f2f71696974612d696d6167652d73746f72652e73332e616d617a6f6e6177732e636f6d2f302f373132332f31303237326264332d666663312d623566352d336463382d3131633261306262383139622e706e67" height="200"/>
</th>
</tr>
</table>

##  requirement
* Raspberry Pi
* python 3.5系のインストール

## セットアップ

Thermal Cameraのの為の準備は[この記事](https://learn.adafruit.com/adafruit-amg8833-8x8-thermal-camera-sensor/raspberry-pi-thermal-camera)と[この記事](https://qiita.com/nobuyukioishi/items/499cb694b2d9286afdc3)を参考

``` sh
pip3 install -r requirements.txt
```

## yamlの設定

* config_sample.yamlをsettings.yamlにリネームして.xxxxxxとなっている所を保管してください
* settings_sample.yamlをsettings.yamlにリネームして.xxxxxxとなっている所を保管してください
