# ForTaiwan_odoo

使用步驟：
1. clone 此專案
2. docker pull a26796879/fortaiwan_odoo:latest  
   或是 cd進入BuildDockerImage   自行建立docker images  
   docker build -t a26796879/fortaiwan_odoo .
3. docker-compose up 以image設定，建立docker container
4. localhost:8069 進入odoo介面進行初始設定
5. 安裝相關模組
6. 進入 config_token 分頁，新建一筆record，環境=here，token=申請到的Line Notify Token
7. 可以依個人需求調整排程時間
