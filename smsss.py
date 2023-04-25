from itertools import product
import os
import discord
import requests
from discord.ext import commands
from dotenv import load_dotenv
from app.PayPay import PayPay
import asyncio
import datetime
from discord.ui import View
import traceback
from discord.commands import Option
import random
from random import randint,randrange

#注意事項
#認証サービスは5simを使います


discord_bot_token = 'MTA5NzU1MzMwMjY0MTcxMzE5Mg.Go1_HC.Od2Jd9qx6yt__JMG0w8Wih4URmVjSPRWSa8ViE'
paypay_token_main = '469f5b90-a95a-4904-87d7-06d71438c372'
sms_api_key = 'eyJhbGciOiJSUzUxMiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MDk3MTg0NTEsImlhdCI6MTY3ODE4MjQ1MSwicmF5IjoiMTUwYmI5YmM3ZWExZTlmMGZkNjE3YmVjOTFjOGNjNGEiLCJzdWIiOjE0NDU4MDZ9.gmBwVf1N403DKtEmQ_a-lLO4kS_JKKffWhT9q1MAv-E22pHm5V92c-xM3ojKCzgATNr3BmQvyu_1FXZJxCTGjXk6Xf-ImAx-J3lyP-wFkc-1RkkvBoO-O7jQ3iGG1KG5oMF7ERPslh7bRMq-7Ys3Imv9Z1CaH3-A2j0wn5luNTNYjU0P8pp5Qmyvd53wEDRi80sVCN4OwF-uJkgxIBh38Cl0HbdzLyMw5GPCxzRQC8jKwyguIVJLybg1UM2lmlGct6ViCseM5axurajtLHD4e82bZBvEVDK59h821HdJTeOlRrhSMYog7o66X3rhSuYSQh3CIlh1cX1Fehwc7P59pg'

Line_price = '50'
Twitter_vietnam_price = '50'
Twitter_usa_price = '50'
Instagram_price = '50'
Tinder_price = '50'
Telegram_price = '50'
Tiktok_price = '50'

#最大チケット数の制限
max_ticket = 3
#webhook_url
webhook_url_admin = 'https://discord.com/api/webhooks/1100071587190952087/FWaC5xUpLs4SGCS8677RspQ8EDumctUwwsx4ei4NcXim_xnXrPC-AdL_5UfjaPC0QrZP'
webhook_url_public = 'https://discord.com/api/webhooks/1100071719168917554/x6VQuFLxCq15a0cmojO4gPGmeRRqE9avfs97IQ3iCnrxc-eap8F0qzdiFm9lRAQMENH2'

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


class sms:
    # 初期設定
    def __init__(self):
        self.api_key = sms_api_key

    # 電話番号を購入
    def buy(self, product):
        try:
            headers = {
                'Authorization': 'Bearer ' + self.api_key,
                'Accept': 'application/json',
            }
            if  str(product) == "Tinder" or str(product) == "tinder":
                country = 'thailand'
                response = requests.get(
                    'https://5sim.net/v1/user/buy/activation/' + str(country) + '/' + 'any' + '/' + str(product),
                    headers=headers)
                
            elif str(product) == "twitter vietnam":
                country = 'vietnam'
                response = requests.get(
                    'https://5sim.net/v1/user/buy/activation/' + str(country) + '/' + 'any' + '/' + 'twitter',
                    headers=headers)
            
            elif str(product) == "twitter usa":
                country = 'usa'
                response = requests.get(
                    'https://5sim.net/v1/user/buy/activation/' + str(country) + '/' + 'any' + '/' + 'twitter',
                    headers=headers)
                    
            else:
                country = 'usa'
                response = requests.get(
                    'https://5sim.net/v1/user/buy/activation/' + str(country) + '/' + 'any' + '/' + "tinder",
                    headers=headers)
     
            if response:
                return {"order_id": str(response.json()["id"]),
                        "phone": str(response.json()["phone"]),
                        "price": str(response.json()["price"]),
                        "expires": str(response.json()["expires"]),
                        }
            else:
                return False
        except:
            return False

    # smsを見る
    def get_sms(self, order_id):
        try:
            headers = {
                'Authorization': 'Bearer ' + self.api_key,
                'Accept': 'application/json',
            }

            response = requests.get('https://5sim.net/v1/user/check/' + str(order_id), headers=headers)
            if response:
                return list(response.json()["sms"])
            else:
                return False
        except:
            return False

    # フィニッシュ
    def finish(self, order_id):
        try:
            headers = {
                'Authorization': 'Bearer ' + self.api_key,
                'Accept': 'application/json',
            }

            response = requests.get('https://5sim.net/v1/user/finish/' + str(order_id), headers=headers)
            if response:
                return True
            else:
                return False
        except:
            return False






#paypay入力モーダル
class payment_modal_sms(discord.ui.Modal):
    def __init__(self, product, price, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.product = product
        self.price = price
        self.add_item(discord.ui.InputText(label="PayPayリンクを入力して下さい。", style=discord.InputTextStyle.short))
        self.add_item(
            discord.ui.InputText(label="パスワードを入力して下さい。", style=discord.InputTextStyle.short, required=False,))

    async def callback(self, interaction: discord.Interaction):
        try:
            print(f"購入サービス{self.product} : 値段{self.price} ")
            paypay_link_data = PayPay.get_link(str(self.children[0].value).split("/")[3])
            # 受け取れるか確認
            if paypay_link_data["payload"]["orderStatus"] == "PENDING":
                #受け取り確認
                if str(self.price) == str(paypay_link_data["payload"]["pendingP2PInfo"]["amount"]):
                    #パスなし
                    if len(self.children[1].value) == 0:
                        await interaction.response.send_message(embed=discord.Embed(title="処理中", color=0x2f3136))
                        paypay_accept_link_data = PayPay.accept_link(str(self.children[0].value).split("/")[3])
                        
                        if not paypay_accept_link_data:
                            await interaction.edit_original_message(
                                embed=discord.Embed(title="このリンクは受け取れません", color=0xff0000))
                            print("PayPay受け取り失敗")
                        else:
                            
                            sms_buy_data = sms.buy(self=sms(),product=self.product)
                            print(sms_buy_data)
                            #buyデータ確認
                            if not sms_buy_data:
                                embed = discord.Embed(title="エラー",description="電話番号が購入出来ませんでした。\n電話番号の在庫がない可能性があります。\nこのスクリーンショットを撮影し、サポートサーバーまで問い合わせをお願いします。", color=0xff0000)
                                embed.add_field(name="購入サービス",value=self.product)
                                embed.add_field(name="決済ID",value=f"{str(paypay_link_data['payload']['pendingP2PInfo']['orderId'])}",inline=False)
                                embed.add_field(name="金額",value=f"{str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円")
                                embed.add_field(name="送金者名",value=f"{str(paypay_link_data['payload']['sender']['displayName'])}",inline=False)
                                await interaction.edit_original_response(
                                    embed=embed)
                                
                            
                                print(f"電話番号購入失敗 : {self.product} : {str(paypay_link_data['payload']['pendingP2PInfo']['orderId'])} : {str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円 : {str(paypay_link_data['payload']['sender']['displayName'])}")
                            else:
                                #webhookで購入履歴の送信
                                webhook_data_admin = {
                                    "username": "購入履歴",
                                    "embeds": [
                                        {
                                            "title": "購入履歴",
                                            "description": f"購入者ユーザー名: {interaction.user.name}\nDiscordID: {interaction.user.id}\nPayPayID: {str(paypay_link_data['payload']['sender']['displayName'])}\n決済ID: {str(paypay_link_data['payload']['pendingP2PInfo']['orderId'])}\n支払い金額: {str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円\n認証サービス: {str(self.product)}"}]}
                                webhook_resp_admin = requests.post(webhook_url_admin,
                                                                headers={'Authorization': f'Bot {discord_bot_token}',
                                                                        'Content-Type': 'application/json'},
                                                                json=webhook_data_admin)
                                webhook_data_public = {
                                    "username": "購入履歴",
                                    "embeds": [
                                        {
                                            "title": "購入履歴",
                                            "description": f"支払い金額: {str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円\n認証サービス: {str(self.product)}"}]}
                                webhook_resp_public = requests.post(webhook_url_public,
                                                                headers={'Authorization': f'Bot {discord_bot_token}',
                                                                        'Content-Type': 'application/json'},
                                                                json=webhook_data_public)
                                #webhook応答確認
                                if webhook_resp_admin and webhook_resp_public:
                                        print(f"購入者ユーザー名: {interaction.user.name} DiscordID: {interaction.user.id} PayPayID: {str(paypay_link_data['payload']['sender']['displayName'])}\n決済ID: {str(paypay_link_data['payload']['pendingP2PInfo']['orderId'])} 支払い金額: {str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円 \n認証サービス: {str(self.product)}")
                                        #finishボタン
                                        async def finish_button_callback_2(interaction3):
                                            try:
                                                sms_finish_data = sms.finish(self=sms(), order_id=sms_buy_data['order_id'])
                                                if sms_finish_data:
                                                    await interaction3.response.send_message(
                                                        embed=discord.Embed(title="取引完了",
                                                                            description="ご利用いただきありがとうございます。\n3秒後にチケットは削除されます。",
                                                                            color=0xff0000))
                                                    await asyncio.sleep(3)
                                                    await interaction3.channel.delete()
                                                if not sms_finish_data:
                                                    await interaction3.response.send_message(
                                                        embed=discord.Embed(title="エラー", color=0xff0000))
                                            except:
                                                await interaction3.response.send_message(
                                                    embed=discord.Embed(title="エラー", color=0xff0000))
                                        #smsログ取得ボタン
                                        async def get_sms_button_callback_2(interaction4):
                                            get_sms_data = sms.get_sms(self=sms(), order_id=sms_buy_data['order_id'])
                                            if not get_sms_data:
                                                await interaction4.response.send_message(
                                                    embed=discord.Embed(title="エラー", description="SMSログを確認できません。",
                                                                        color=0xff0000))
                                            else:
                                                if len(get_sms_data) == 0:
                                                    await interaction4.response.send_message(
                                                        embed=discord.Embed(title="何も受信していません。",
                                                                            color=0xff0000))

                                                code_list = []
                                                for index, item in enumerate(get_sms_data):
                                                    code_list.append(item["code"])
                                                    
                                                embed = discord.Embed(title="SMSログ", color=0x2f3136)
                                                embed.add_field(name="order_id", value=str(sms_buy_data['order_id']),
                                                                inline=False)
                                                embed.add_field(name="コード", value=str(code_list).strip("[]"),
                                                            inline=False)
                                                await interaction4.response.send_message(embed=embed)
                                        #キャンセルボタン        
                                        async def cancel_sms_button_callback(interaction14):
                                            sms_cancel_status = sms_buy.cancel(self=sms_buy(), order_id=sms_buy_data['order_id'])
                                            if not sms_cancel_status:
                                                await interaction14.response.send_message(embed=discord.Embed(title="キャンセルできませんでした",color=0xff0000))
                                            else:
                                                await interaction14.response.send_message(embed=discord.Embed(title="正常にキャンセルされました",color=0x00ff11))    
                        
            
                                        cancel_sms = discord.ui.Button(label="キャンセルする",style=discord.ButtonStyle.danger)
                                        cancel_sms.callback = cancel_sms_button_callback
                                        #キャンセル確認ボタン
                                        async def cancel_sms_check_button_callback(interaction15):
                                            view = View(timeout=None)
                                            view.add_item(cancel_sms)
                                            
                                            await interaction15.response.send_message(embed=discord.Embed(title="キャンセル",
                                                                                                        description="注文がキャンセルされます。\n実行後の返金対応などは行えません。",
                                                                                                        color=0xff0000),
                                                                                    view=view,)
                                        #購入用のログファイルの書き込み
                                        f = open('buy_log.txt', 'a')
                                        f.write(
                                            f"購入者ユーザー名: {interaction.user.name}|購入者ID: {interaction.user.id}|支払い金額: {str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円|認証サービス: {str(self.product)}\n")
                                        f.close()
                                        #購入完了メッセージ送信
                                        embed = discord.Embed(title="購入完了", color=0x00ff11)
                                        embed.add_field(name="order_id", value=f"`{sms_buy_data['order_id']}`",
                                                        inline=False)
                                        embed.add_field(name="決済ID",value=f"{str(paypay_link_data['payload']['pendingP2PInfo']['orderId'])}",inline=False)
                                        embed.add_field(name="金額",value=f"{str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円")
                                        embed.add_field(name="送金者名",value=f"{str(paypay_link_data['payload']['sender']['displayName'])}",inline=False)
                                        embed.add_field(name="電話番号",value=f"{sms_buy_data['phone']}",inline=False)
                                        embed.add_field(name="期限", value=f"{sms_buy_data['expires']}", inline=False)
                                        embed.set_footer(text="別で送られてくる電話番号をコピーして認証を行ってください。")
                                        #各ボタン定義
                                        finish_button_2 = discord.ui.Button(label="完了",
                                                                            style=discord.ButtonStyle.green)
                                        finish_button_2.callback = finish_button_callback_2
                                        get_sms_button_2 = discord.ui.Button(label="SMSのログを確認する",
                                                                            style=discord.ButtonStyle.primary)
                                        get_sms_button_2.callback = get_sms_button_callback_2
                                        
                                        cancel_sms_check_button = discord.ui.Button(label="キャンセル",style=discord.ButtonStyle.danger)
                                        cancel_sms_check_button.callback = cancel_sms_check_button_callback       
                                        view = View()
                                        view.add_item(finish_button_2)
                                        view.add_item(get_sms_button_2)
                                        view.add_item(cancel_sms_check_button)
                                        await interaction.edit_original_response(embed=embed,view=view)
                                        await interaction.followup.send(f"{sms_buy_data['phone']}")
                                        await asyncio.sleep(600)
                                        if len(sms.get_sms(self=sms(), order_id=sms_buy_data['order_id'])) == 0:
                                            await interaction.followup.send(embed=discord.Embed(title="タイムアウト",description="これ以降この番号を使用した認証は行えません。番号を再購入してください。",color=0xff0000))
                                        else:
                                            return
                                else:
                                    await interaction.edit_original_response(
                                        embed=discord.Embed(title="エラー", color=0xff0000))
                                    
                                    
                                    
                                    
                                    
                # パスコードあり(受け取り部分以外は上と同じ)
                    else:
                        await interaction.response.send_message(embed=discord.Embed(title="処理中", color=0x2f3136))
                        paypay_accept_link_data = PayPay.accept_link(str(self.children[0].value).split("/")[3],str(self.children[1].value))
                        if not paypay_accept_link_data:
                            await interaction.edit_original_response(
                                embed=discord.Embed(title="このリンクは受け取れません", color=0xff0000))
                            print("PayPay受け取り失敗 ")
                        else:
                            sms_buy_data = sms.buy(self=sms(), product=self.product)
                            print(sms_buy_data)
                            if not sms_buy_data:
                                embed = discord.Embed(title="エラー",description="電話番号が購入出来ませんでした。\n電話番号の在庫がない可能性があります。\nこのスクリーンショットを撮影し、サポートサーバーまで問い合わせをお願いします。", color=0xff0000)
                                embed.add_field(name="購入サービス",value=self.product)
                                embed.add_field(name="決済ID",value=f"{str(paypay_link_data['payload']['pendingP2PInfo']['orderId'])}",inline=False)
                                embed.add_field(name="金額",value=f"{str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円")
                                embed.add_field(name="送金者名",value=f"{str(paypay_link_data['payload']['sender']['displayName'])}",inline=False)
                                await interaction.edit_original_response(
                                    embed=embed)
                                print(f"電話番号購入失敗 : {self.product} : {str(paypay_link_data['payload']['pendingP2PInfo']['orderId'])} : {str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円 : {str(paypay_link_data['payload']['sender']['displayName'])}")
                            else:
                                webhook_data_admin = {
                                    "username": "購入履歴",
                                    "embeds": [
                                        {
                                            "title": "購入履歴",
                                            "description": f"購入者ユーザー名: {interaction.user.name}\nDiscordID: {interaction.user.id}\nPayPayID: {str(paypay_link_data['payload']['sender']['displayName'])}\n決済ID: {str(paypay_link_data['payload']['pendingP2PInfo']['orderId'])}\n支払い金額: {str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円\n認証サービス: {str(self.product)}"}]}
                                webhook_resp_admin = requests.post(webhook_url_admin,
                                                                headers={'Authorization': f'Bot {discord_bot_token}',
                                                                        'Content-Type': 'application/json'},
                                                                json=webhook_data_admin)
                                webhook_data_public = {
                                    "username": "購入履歴",
                                    "embeds": [
                                        {
                                            "title": "購入履歴",
                                            "description": f"支払い金額: {str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円\n認証サービス: {str(self.product)}"}]}
                                webhook_resp_public = requests.post(webhook_url_public,
                                                                headers={'Authorization': f'Bot {discord_bot_token}',
                                                                        'Content-Type': 'application/json'},
                                                                json=webhook_data_public)
                                if webhook_resp_admin and webhook_resp_public:
                                    print(f"購入者ユーザー名: {interaction.user.name} DiscordID: {interaction.user.id} PayPayID: {str(paypay_link_data['payload']['sender']['displayName'])}\n決済ID: {str(paypay_link_data['payload']['pendingP2PInfo']['orderId'])} 支払い金額: {str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円 \n認証サービス: {str(self.product)}")
                                    async def finish_button_callback_1(interaction3):
                                            try:
                                                sms_finish_data = sms.finish(self=sms(), order_id=sms_buy_data['order_id'])
                                                if sms_finish_data:
                                                    await interaction3.response.send_message(
                                                        embed=discord.Embed(title="取引完了",
                                                                            description="ご利用いただきありがとうございます。\n3秒後にチケットは削除されます。",
                                                                            color=0xff0000))
                                                    await asyncio.sleep(3)
                                                    await interaction3.channel.delete()
                                                if not sms_finish_data:
                                                    await interaction3.response.send_message(
                                                        embed=discord.Embed(title="エラー", color=0xff0000))
                                            except:
                                                await interaction3.response.send_message(
                                                    embed=discord.Embed(title="エラー", color=0xff0000))

                                    async def get_sms_button_callback_1(interaction4):
                                            get_sms_data = sms.get_sms(self=sms(), order_id=sms_buy_data['order_id'])
                                            if not get_sms_data:
                                                await interaction4.response.send_message(
                                                    embed=discord.Embed(title="エラー", description="SMSログを確認できません。",
                                                                        color=0xff0000))
                                            else:
                                                if len(get_sms_data) == 0:
                                                    await interaction4.response.send_message(
                                                        embed=discord.Embed(title="何も受信していません。",
                                                                            color=0xff0000))

                                                code_list = []
                                            for index, item in enumerate(get_sms_data):
                                                code_list.append(item["code"])
                                                embed = discord.Embed(title="SMSログ", color=0x2f3136)
                                                embed.add_field(name="order_id", value=str(sms_buy_data['order_id']),
                                                                inline=False)
                                                embed.add_field(name="コード", value=str(code_list).strip("[]"),
                                                            inline=False)
                                                await interaction4.response.send_message(embed=embed)
                                    async def cancel_sms_button_callback(interaction16):
                                            sms_cancel_status = sms_buy.cancel(self=sms_buy(), order_id=sms_buy_data['order_id'])
                                            if not sms_cancel_status:
                                                await interaction16.response.send_message(embed=discord.Embed(title="キャンセルできませんでした",color=0xff0000))
                                            else:
                                                await interaction16.response.send_message(embed=discord.Embed(title="正常にキャンセルされました",color=0x00ff11))    
                        
            
                                    cancel_sms = discord.ui.Button(label="キャンセルする",style=discord.ButtonStyle.danger)
                                    cancel_sms.callback = cancel_sms_button_callback
                        
                                    async def cancel_sms_check_button_callback(interaction17):
                                            view = View(timeout=None)
                                            view.add_item(cancel_sms)
                                            
                                            await interaction17.response.send_message(embed=discord.Embed(title="キャンセル",
                                                                                                        description="注文がキャンセルされます。\n実行後の返金対応などは行えません。",
                                                                                                        color=0xff0000),
                                                                                    view=view,)
                                            
                                        # テキストファイルは生成されてますか？
                                    f = open('buy_log.txt', 'a')
                                    f.write(
                                            f"購入者ユーザー名: {interaction.user.name}|購入者ID: {interaction.user.id}|支払い金額: {str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円|認証サービス: {str(self.product)}\n")
                                    f.close()
                                    embed = discord.Embed(title="購入完了", color=0x00ff11)
                                    embed = discord.Embed(title="購入完了", color=0x00ff11)
                                    embed.add_field(name="order_id", value=f"`{sms_buy_data['order_id']}`",
                                                        inline=False)
                                    embed.add_field(name="決済ID",value=f"{str(paypay_link_data['payload']['pendingP2PInfo']['orderId'])}",inline=False)
                                    embed.add_field(name="金額",value=f"{str(paypay_link_data['payload']['pendingP2PInfo']['amount'])}円")
                                    embed.add_field(name="送金者名",value=f"{str(paypay_link_data['payload']['sender']['displayName'])}",inline=False)
                                    embed.add_field(name="電話番号",value=f"{sms_buy_data['phone']}",inline=False)
                                    embed.add_field(name="期限", value=f"{sms_buy_data['expires']}", inline=False)
                                    embed.set_footer(text="別で送られてくる電話番号をコピーして認証を行ってください。")
                                    finish_button_1 = discord.ui.Button(label="完了",
                                                                            style=discord.ButtonStyle.green)
                                    finish_button_1.callback = finish_button_callback_1
                                    get_sms_button_1 = discord.ui.Button(label="SMSのログを確認する",
                                                                            style=discord.ButtonStyle.primary)
                                    get_sms_button_1.callback = get_sms_button_callback_1
                                    cancel_sms_check_button = discord.ui.Button(label="キャンセル",style=discord.ButtonStyle.danger)
                                    cancel_sms_check_button.callback = cancel_sms_check_button_callback       
                                    view = View()
                                    view.add_item(finish_button_1)
                                    view.add_item(get_sms_button_1)
                                    view.add_item(cancel_sms_check_button)
                                    await interaction.edit_original_response(embed=embed,view=view)
                                    await interaction.followup.send(f"{sms_buy_data['phone']}")
                                    await asyncio.sleep(600)
                                    if len(sms.get_sms(self=sms(), order_id=sms_buy_data['order_id'])) == 0:
                                        await interaction.followup.send(embed=discord.Embed(title="タイムアウト",description="これ以降この番号を使用した認証は行えません。番号を再購入してください。",color=0xff0000))
                                    else:
                                        return
                                else:
                                    await interaction.edit_original_response(
                                            embed=discord.Embed(title="エラー", color=0xff0000))
                else:
                    await interaction.response.send_message(embed=discord.Embed(title="金額が一致しません。", color=0xff0000))
            else:
                await interaction.response.send_message(embed=discord.Embed(title="このリンクは受け取れません", color=0xff0000))
        except:
             await interaction.edit_original_response(embed=discord.Embed(title="原因不明のエラー", color=0xff0000))
            






#smsサービス選択
class purchase_select_menu_sms(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(custom_id="purchase_select_menu",
                       placeholder="サービスを選択してください。",
                       min_values=1,
                       max_values=1,
                       options=[
                           discord.SelectOption(
                               label="Twitter usa",
                               description=f"{Twitter_usa_price}円"
                            ),
                           discord.SelectOption(
                               label="Twitter vietnam",
                               description=f"{Twitter_vietnam_price}円"
                            ),
                           discord.SelectOption(
                               label="Line",
                               description=f"{Line_price}円"
                           ),
                           discord.SelectOption(
                               label="Instagram",
                               description=f"{Instagram_price}円"
                           ),
                           discord.SelectOption(
                               label="Tinder",
                               description=f"{Tinder_price}円"
                           ),
                           discord.SelectOption(
                               label="Telegram",
                               description=f"{Telegram_price}円"
                            ),
                           discord.SelectOption(
                               label="Tiktok",
                               description=f"{Tiktok_price}円"
                               )])
    
    
    async def select_callback_sms(self, select,
                              interaction):
        if str(select.values[0]) == "Line":
            Line_embed = discord.Embed(title="LineSMS認証", color=0x11ff00)
            Line_embed.add_field(name="値段", value=f"{Line_price}", inline=False)
            modal = payment_modal_sms(title=f"{Line_price}円の支払い", product=str(select.values[0]).lower(),
                                  price=Line_price)
            await interaction.response.send_modal(modal)
        if str(select.values[0]) == "Twitter vietnam":
            Line_embed = discord.Embed(title="TwitterSMS認証", color=0x11ff00)
            Line_embed.add_field(name="値段", value=f"{Twitter_vietnam_price}円", inline=False)
            modal = payment_modal_sms(title=f"{Twitter_vietnam_price}円の支払い", product="twitter vietnam",
                                  price=Twitter_vietnam_price)
            await interaction.response.send_modal(modal)
        if str(select.values[0]) == "Twitter usa":
            Line_embed = discord.Embed(title="TwitterSMS認証", color=0x11ff00)
            Line_embed.add_field(name="値段", value=f"{Twitter_usa_price}円", inline=False)
            modal = payment_modal_sms(title=f"{Twitter_usa_price}円の支払い", product="twitter usa",
                                  price=Twitter_usa_price)
            await interaction.response.send_modal(modal)
        if str(select.values[0]) == "Instagram":
            Line_embed = discord.Embed(title="InstagramSMS認証", color=0x11ff00)
            Line_embed.add_field(name="値段", value=f"{Instagram_price}円", inline=False)
            modal = payment_modal_sms(title=f"{Instagram_price}円の支払い", product=str(select.values[0]).lower(),
                                  price=Instagram_price)
            await interaction.response.send_modal(modal)
        if str(select.values[0]) == "Tinder":
            Line_embed = discord.Embed(title="TinderSMS認証", color=0x11ff00)
            Line_embed.add_field(name="値段", value=f"{Tinder_price}円", inline=False)
            modal = payment_modal_sms(title=f"{Tinder_price}円の支払い", product=str(select.values[0]).lower(),
                                  price=Tinder_price)
            await interaction.response.send_modal(modal)
        if str(select.values[0]) == "Telegram":
            Line_embed = discord.Embed(title="TelegramSMS認証", color=0x11ff00)
            Line_embed.add_field(name="値段", value=f"{Telegram_price}円", inline=False)
            modal = payment_modal_sms(title=f"{Telegram_price}円の支払い", product=str(select.values[0]).lower(),
                                  price=Telegram_price)
            await interaction.response.send_modal(modal)
        if str(select.values[0]) == "Tiktok":
            Line_embed = discord.Embed(title="TiktokSMS認証", color=0x11ff00)
            Line_embed.add_field(name="値段", value=f"{Tiktok_price}円", inline=False)
            modal = payment_modal_sms(title=f"{Tiktok_price}円の支払い", product=str(select.values[0]).lower(),
                                  price=Tiktok_price)
            await interaction.response.send_modal(modal)
            
            
#チケット削除ボタン
class ticket_delete_button(discord.ui.View):
    
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="チケットを閉じる",custom_id="ticket_delete_button",style=discord.ButtonStyle.red)
    async def delete_button_callback_1(self, button,interaction5):
            await interaction5.response.send_message(
                embed=discord.Embed(title="チケット削除",
                                    description="チケットは3秒後に削除されます。",
                                    color=0xff0000))
            await asyncio.sleep(3)
            await interaction5.channel.delete()


#管理者用コマンド
class sms_buy:
    
    def __init__(self):
        self.api_key = sms_api_key
        
        
    def buy(self,country,service):
        try:
            headers = {
                        'Authorization': 'Bearer ' + sms_api_key,
                        'Accept': 'application/json',
                    }
            response = requests.get('https://5sim.net/v1/user/buy/activation/' + str(country) + '/' + 'any' + '/' + str(service),headers=headers)
            if response:
                return {"order_id": str(response.json()["id"]),
                        "phone": str(response.json()["phone"]),
                        "price": str(response.json()["price"]),
                        "expires": str(response.json()["expires"])
                            }
            else:
                return False
        except:
            return False
            
    def get_sms(self, order_id):
        try:
            headers = {
                'Authorization': 'Bearer ' + self.api_key,
                'Accept': 'application/json',
            }

            response = requests.get('https://5sim.net/v1/user/check/' + str(order_id), headers=headers)
            if response:
                return list(response.json()["sms"])
            else:
                return False
        except:
            return False

    # フィニッシュ
    def finish(self, order_id):
        try:
            headers = {
                'Authorization': 'Bearer ' + self.api_key,
                'Accept': 'application/json',
            }

            response = requests.get('https://5sim.net/v1/user/finish/' + str(order_id), headers=headers)
            if response:
                return True
            else:
                return False
        except:
            return False
        
        
        
    def cancel(self,order_id):
        try:
            headers = {
                'Authorization': 'Bearer ' + self.api_key,
                'Accept': 'application/json',
            }
            response = requests.get('https://5sim.net/v1/user/cancel/' + str(order_id), headers=headers)
            if response:
                return True
            else:
                return False
        except:
            return False


#管理者用再購入コマンド          
            
@bot.command(description="bot管理者専用 SMS購入 ",administrator=True)
@commands.has_permissions(administrator = True)
async def buy_sms(ctx,service:Option(str,"サービス名",required = True, default =""),country:Option(str,"国",required = True, default ="")):
        sms_buy_data = sms_buy.buy(self=sms_buy(),service=service,country=country)
        print(sms_buy_data)
        if not sms_buy_data:
            await ctx.respond(embed=discord.Embed(title="エラー", description="電話番号が購入出来ません。\n電話番号の在庫がない可能性があります。\n管理者をメンションすることで在庫の確認、対応を行います。",color=0xff0000))
            print("電話番号購入失敗")
        else:                 
            
            #上の処理のpaypay受け取り部分削除しただけ
            async def finish_button_callback_3(interaction8):
                try:
                    sms_finish_data = sms_buy.finish(self=sms_buy(), order_id=sms_buy_data['order_id'])
                    print(sms_finish_data)
                    if sms_finish_data:
                        await interaction8.response.send_message(embed=discord.Embed(title="取引完了",color=0xff0000))
                        
                    else:
                        await interaction8.response.send_message(embed=discord.Embed(title="エラー",color=0xff0000))
                except:
                    await interaction8.response.send_message(embed=discord.Embed(title="エラー", color=0xff0000))
            
                    
            async def get_sms_button_callback_4(interaction9):
                get_data = sms_buy.get_sms(self=sms_buy(), order_id=sms_buy_data['order_id'])
                print(get_data)
                if not get_data:
                    await interaction9.response.send_message(embed=discord.Embed(title="コードを受信していません。"))
                                                                                                
                else:
                    if len(get_data) == 0:
                        await interaction9.response.send_message(embed=discord.Embed(title="何も受信していません。",color=0xff0000))
                        
                    code_list = []
                    for index, item in enumerate(get_data):
                        code_list.append(item["code"])
                                                                
                    embed = discord.Embed(title="SMSログ", color=0x2f3136)
                    embed.add_field(name="order_id", value=str(sms_buy_data['order_id']),
                                                                            inline=False)
                    embed.add_field(name="コード", value=str(code_list).strip("[]"),
                                                                        inline=False)
                    await interaction9.response.send_message(embed=embed)   
            
            async def cancel_sms_button_callback(interaction13):
                    sms_cancel_status = sms_buy.cancel(self=sms_buy(), order_id=sms_buy_data['order_id'])
                    if not sms_cancel_status:
                        await interaction13.response.send_message(embed=discord.Embed(title="キャンセルできませんでした",color=0xff0000))
                    else:
                        await interaction13.response.send_message(embed=discord.Embed(title="正常にキャンセルされました",color=0x00ff11))    
                        
            
            cancel_sms = discord.ui.Button(label="キャンセルする",style=discord.ButtonStyle.danger)
            cancel_sms.callback = cancel_sms_button_callback
                        
            async def cancel_sms_check_button_callback(interaction12):
                view = View(timeout=None)
                view.add_item(cancel_sms)
                
                await interaction12.response.send_message(embed=discord.Embed(title="キャンセル",
                                                                              description="注文がキャンセルされます。\n実行後の返金対応などは行えません。",
                                                                              color=0xff0000),
                                                          view=view,
                                                          ephemeral=True)
                                         
            embed = discord.Embed(title="購入 管理者パネル", color=0x00ff11)
            embed.add_field(name="国",value=country,inline=False)
            embed.add_field(name="サービス",value=service,inline=False)
            embed.add_field(name="order_id", value=f"`{sms_buy_data['order_id']}`",inline=False)
            embed.add_field(name="電話番号", value=f"{sms_buy_data['phone']}", inline=False)
            embed.add_field(name="期限", value=f"{sms_buy_data['expires']}", inline=False)
            embed.set_footer(text="Develop by fork",
                        icon_url="https://cdn.discordapp.com/avatars/1031132130547351622/b672a961f463fc82b6a1d0641af55b91.webp?size=128")
            
            cancel_sms_check_button = discord.ui.Button(label="キャンセル",style=discord.ButtonStyle.danger)
            cancel_sms_check_button.callback = cancel_sms_check_button_callback        
            finish_button_3 = discord.ui.Button(label="完了",style=discord.ButtonStyle.green)
            finish_button_3.callback = finish_button_callback_3
            get_sms_button_4 = discord.ui.Button(label="SMSログを確認する",style=discord.ButtonStyle.primary)
            get_sms_button_4.callback = get_sms_button_callback_4
            view = View(timeout=None)
            view.add_item(finish_button_3)
            view.add_item(get_sms_button_4)
            view.add_item(cancel_sms_check_button)
            
            await ctx.respond(embed=embed, view=view)
            await ctx.respond(f"{sms_buy_data['phone']}")
            await asyncio.sleep(600)
            if len(sms.get_sms(self=sms(), order_id=sms_buy_data['order_id'])) == 0:
                await ctx.respond(embed=discord.Embed(title="タイムアウト",color=0xff0000))
            else:
                return
   



       
# 購入ボタン
class purchase_button_sms(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    #購入ボタン
    @discord.ui.button(label="購入する", custom_id="purchase_button_sms", style=discord.ButtonStyle.success)
    async def button_callback(self, button, interaction):
        #チケット作成
        ticket_name = f"🎫-{interaction.user.name}"
        #チケット数の確認
        if len([i for i in interaction.guild.channels if i.name == ticket_name]) >= max_ticket:
            await interaction.response.send_message(embed=discord.Embed(title="チケットを開きすぎています", color=0xff0000),
                                                    ephemeral=True)
            return
        #カテゴリ確認
        category_id = interaction.custom_id.replace('create', '')
        category = interaction.guild.get_channel(category_id)
        if category is None:
            
            category = discord.utils.get(interaction.guild.categories, name='チケット')
            #なければ作成
            if category is None:
                await interaction.guild.create_category("チケット")
                category = discord.utils.get(interaction.guild.categories, name='チケット')
        guild = bot.get_guild(interaction.guild.id)
        #チケットの権限設定
        permission = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
        }
        ticket_ch = await category.create_text_channel(name=f"{ticket_name}", overwrites=permission)
        #チケット削除ボタン
        delete_button_1 = discord.ui.Button(label="チケットを閉じる",custom_id="delete_button",style=discord.ButtonStyle.red)
        delete_button_1.callback = ticket_delete_button.delete_button_callback_1
        #メッセージ、メニュー、チケット削除ボタンを送信
        await interaction.response.send_message(embed=discord.Embed(title="お問い合わせチャンネルを作成しました", color=0x2f3136),
                                                ephemeral=True)
        
        await ticket_ch.send(interaction.user.mention,
                             embed=discord.Embed(title="SMS認証購入", description="下記のメニューから使用するサービスを選択してください。",
                                                 color=0x2f3136), view=purchase_select_menu_sms())
        await ticket_ch.send(view=ticket_delete_button())

    #サポートサーバーボタン
    @discord.ui.button(label="サポートサーバー",custom_id="support_button",style=discord.ButtonStyle.primary)
    async def support_button_callback(self,button,interaction):
        await interaction.response.send_message("サポートサーバーはこちらです。\nサーバー内のチケットに支払いが完了しているという証拠とともにお問い合わせください。\nhttps://discord.gg/yzyEQCtwbf", ephemeral=True)
        
        
        
# sms認証パネル設置コマンド
@bot.command(description="電話番号認証パネルを設置します。", administrator=True)
@commands.has_permissions(administrator = True)
async def sms_panel(ctx):
    embed = discord.Embed(title="電話番号認証", description="24時間いつでも電話番号認証(SMS認証)をすることができます", colour=0x2f3136)
    embed.add_field(name="認証について",value="```認証には基本アメリカの番号を使用します。\n国番号を+1(アメリカ合衆国)に変更して認証してください。\n```",inline=False)
    embed.add_field(name="Twitter認証について",value="```Twitterにはvietnam認証とusa認証の二つを用意しています。\nusa認証の方が安定性が高いです。usa認証の場合は国番号がUnited Status(+1),vietnam認証の場合はVietnam(+84)になります。\nご注意ください。```",inline=False)
    embed.add_field(name="Tinder認証について",value="```Tinder認証ではアメリカ番号での認証が不安定なため、タイ(+66)番号で認証を行います。\n認証時はご注意ください。```",inline=False)
    embed.add_field(name="LINE認証について",value="```LINEの認証は新規登録専用です。ご注意ください```",inline=False)
    embed.add_field(name="認証エラーについて",value="```電話番号を正しく入力していても認証コードが届かない場合があります。\nその場合は決済情報をスクショして、サポートサーバーまで問い合わせをお願いします。```",inline=False)
    embed.add_field(name="タイムアウト",value="```支払いをしてから10分以内に認証をしないとタイムアウトします。\nコードが届かない場合はタイムアウトする前に管理者をメンションしてください。```",inline=False)
    embed.add_field(name="認証エラー時の対応",value="```依頼者側の問題の場合、一切の対応いたしません。\n電話番号を正しく入力していたにも関わらず、認証コードが届かなかった場合は番号の再発行を行います。\nそれでもコードが届かないことが続く、番号の取得が行えなかった場合にのみ返金対応を行います。```",inline=False)
    embed.set_image(url="https://cdn.discordapp.com/attachments/1040600623013441626/1043378478797561876/SMS.png")
    embed.set_footer(text="Develop by fork",
                     icon_url="https://cdn.discordapp.com/avatars/1031132130547351622/b672a961f463fc82b6a1d0641af55b91.webp?size=128")
    
    await ctx.respond(embed=embed, view=purchase_button_sms())
