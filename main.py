import collections
import json
import os
import random
import re
import time
import requests
import pickle

from telebot import types
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from auth_bot import TOKEN, CHANNEL_ID, username, password
from selenium import webdriver
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


class InstagramBot:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        # chrome_options = Options()
        # chrome_options.add_argument('headless')
        # self.driver = webdriver.Chrome(options=chrome_options, executable_path=r'chromedriver')

        options = webdriver.FirefoxOptions()
        options.headless = True
        options.add_argument("start-maximized")
        options.add_argument("disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-application-cache')
        options.add_argument('--disable-gpu')
        options.add_argument("--disable-dev-shm-usage")
        options.set_preference("general.useragent.override",
                               "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36")
        options.set_preference("dom.webdriver.enabled", False)
        self.driver = webdriver.Firefox(executable_path="geckodriver", options=options)
        self.driver.set_window_size(1440, 1040)

    def close_browser(self):
        self.driver.close()
        self.driver.quit()

    def login(self):
        try:
            driver = self.driver
            # driver.get('https://www.instagram.com/')
            #
            # time.sleep(random.randrange(3, 5))
            #
            # username_input = driver.find_element_by_name('username')
            # username_input.clear()
            # username_input.send_keys(username)
            # time.sleep(2)
            # password_input = driver.find_element_by_name('password')
            # password_input.clear()
            # password_input.send_keys(password)
            #
            # password_input.send_keys(Keys.ENTER)
            # time.sleep(5)
            #
            # pickle.dump(driver.get_cookies(), open("cookies", "wb"))
            driver.get('https://www.instagram.com/rukodelnicachara')

            for cookie in pickle.load(open("cookies", "rb")):
                driver.add_cookie(cookie)
            driver.refresh()

        except Exception as ex:
            return ex

    def xpath_exists(self, url):
        browser = self.driver
        try:
            browser.find_element_by_xpath(url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    def photos(self):

        browser = self.driver
        userpage = 'https://www.instagram.com/rukodelnicachara'
        browser.get(userpage)

        while True:
            if browser.execute_script("return document.readyState") == 'complete':
                break

        title_text = browser.find_element_by_xpath("//h1[@class='rhpdm']")
        title = title_text.text
        time.sleep(random.randrange(1, 3))

        # В переменную помешается имя пользователя
        file_name = userpage.split("/")[-1]

        # Существует ли директория с именем пользователя
        if os.path.exists(f"{file_name}"):
            pass
        else:
            os.mkdir(file_name)

        wrong_userpage = "/html/body/div[1]/section/main/div/h2"
        if self.xpath_exists(wrong_userpage):
            return "Такого пользователя не существует, проверьте URL"
        else:
            time.sleep(random.randrange(1, 3))

            hrefs = browser.find_elements_by_tag_name('a')
            hrefs = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

            new_post = hrefs[0:1]

            for href in new_post:

                # Нажимаем на нее
                browser.get(href)
                time.sleep(random.randrange(0.5, 1))

                # Получаем описание к посту
                post_text = browser.find_element_by_xpath("//div[@class='C4VMK']/span")

                text_point = post_text.text.replace(".", "\\.")
                text_question = text_point.replace("!", "\\!").replace("+", "\\+")
                text_dash = text_question.replace("-", "\\-").replace(")", "\\)")
                text_asterisk = text_dash.replace("*", "\\*").replace("(", "\\(")

                print(text_asterisk)

                dog_search = re.search('(?<=@)(.*)', text_asterisk)

                print(dog_search)

                if dog_search is not None:
                    dog_search = dog_search.group().replace("@", "")
                else:
                    print("dog_search is None")

                if dog_search:
                    dog_link = f"https://www\\.instagram\\.com/{dog_search}/"
                    print(dog_link)
                    text_dr = re.sub(r"@", f"в [Инстаграме ]({dog_link})",
                                     text_asterisk)
                # elif olgakuro9042:
                #     link_olgakuro9042 = "https://www\\.instagram\\.com/olgakuro9042/"
                #     text_dr = re.sub(r"@olgakuro9042", f"в Инстаграме [olgakuro9042]({link_olgakuro9042})",
                #                      text_asterisk)
                else:
                    text_dr = text_asterisk
                text_price = re.sub(r"Цена", f"`Цена`", text_dr)
                del_from_end = text_price.partition("Есть вопросы?")[0]
                del_availability = del_from_end.replace("В наличии.", "")
                count_text = 0
                text_des = str()
                len_text = len(del_availability)

                if len_text > 820:
                    for entry in del_availability.split('\n'):
                        count_text += len(entry)
                        if count_text < 820:
                            text_des += f"{entry} \n"
                    add_continuation = f'Продолжение читайте в [Инстаграме]({href})\n\n'
                    text_des_add_con = text_des + add_continuation
                else:
                    text_des_add_con = del_availability

                userpage_main = 'https://www\\.instagram\\.com/rukodelnicachara'

                add_my_text_in_end = '\n\nЕсть вопросы?' \
                                     f'\nПишите в' \
                                     '\n\\- 📪телеграм @rukodelnicachara' \
                                     f'\n\\- 📩директ [{title}]({userpage_main})' \
                                     '\n\\- 📧почта \\(rukodelnica\\.chara@gmail\\.com\\)' \
                                     '\nВсегда рада ответить на ваши вопросы\\.'
                modified_text = text_des_add_con + add_my_text_in_end

                img_src1 = "//div[@class='eLAPa kPFhm']/div[1]/img"
                img_src1_1 = "//div[@class='eLAPa RzuR0']/div[1]/img"
                img_src2 = "//li[3]/div/div/div[@class='eLAPa RzuR0']/div[1]/img"
                button_src = "//div[@class='    coreSpriteRightChevron  ']"
                button_n = "div[class='    coreSpriteRightChevron  ']"

                post_id = href.split("/")[-2]

                # Если фотография одна у поста
                if self.xpath_exists(img_src1):
                    img_src_url = browser.find_element_by_xpath(img_src1).get_attribute("src")
                    get_img = requests.get(img_src_url)

                    if get_img.status_code == 200:
                        # Записываем фотографию
                        with open(f"{file_name}/{file_name}_{post_id}_img1.jpg", "wb") as img_file:
                            img_file.write(get_img.content)
                            file_foto = [img_file.name]
                            time.sleep(random.randrange(2, 4))

                # Если фотографий несколько
                elif self.xpath_exists(img_src1_1):
                    file_foto = []

                    count_foto = 0
                    while True:
                        if browser.find_elements_by_css_selector(button_n):
                            count_foto += 1
                            time.sleep(random.randrange(2, 4))
                            if count_foto == 1:
                                img_src_url = browser.find_element_by_xpath(img_src1_1).get_attribute("src")
                                get_img = requests.get(img_src_url)
                            else:
                                img_src_url = browser.find_element_by_xpath(img_src2).get_attribute("src")
                                get_img = requests.get(img_src_url)

                            # Записываем фотографию
                            with open(f"{file_name}/{file_name}_{post_id}_img{count_foto}.jpg", "wb") as img_file:
                                img_file.write(get_img.content)
                                file_foto += [img_file.name]
                            time.sleep(random.randrange(2, 4))
                            browser.find_element_by_xpath(button_src).click()
                        else:
                            count_foto += 1
                            time.sleep(random.randrange(2, 4))
                            img_src_url = browser.find_element_by_xpath(img_src2).get_attribute("src")
                            get_img = requests.get(img_src_url)
                            with open(f"{file_name}/{file_name}_{post_id}_img{count_foto}.jpg",
                                      "wb") as img_file:
                                img_file.write(get_img.content)
                                file_foto += [img_file.name]
                            break

                else:
                    return "Что не так с фотографиями!"
                return file_foto, modified_text
        self.driver.close()
        self.driver.quit()


im_bot = InstagramBot(username, password)
im_bot.login()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

button1 = types.KeyboardButton("Выгрузить пост!")
markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True).add(button1)


def user(self):
    users = dict(self)
    print(users)
    with open(f"users.json", 'a', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False)
        f.write('\n')


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    user(message)
    user_id = ""
    user_id_bot = message.from_user.username
    if user_id_bot == user_id:
        await message.reply("Привет!\nДоступ разрешен!", reply_markup=markup1)
    else:
        await message.reply("Доступ запрешен! Логи сохранены!!!")


@dp.message_handler(content_types=['text'])
async def echo_message(message: types.Message):
    user(message)
    user_id = ""
    user_id_bot = message.from_user.username
    if user_id_bot == user_id:
        if message.text == 'Выгрузить пост!':
            try:
                str1, str2 = im_bot.photos()
                media_group = types.MediaGroup()

                if str1[1:]:

                    for x in str1[0:1]:
                        media_group.attach_photo(types.InputFile(x), f'{str2}', parse_mode="MarkdownV2")

                    for x in str1[1:]:
                        media_group.attach_photo(types.InputFile(x))

                    await bot.send_media_group(CHANNEL_ID, media_group)
                    await bot.send_message(message.chat.id, "Выгрузил, проверяйте!")

                else:
                    for x in str1:
                        media_group.attach_photo(types.InputFile(x), f'{str2}', parse_mode="MarkdownV2")

                    await bot.send_media_group(CHANNEL_ID, media_group)
                    await bot.send_message(message.chat.id, "Выгрузил, проверяйте!")

            except Exception as ex:
                print(ex)
                str1 = im_bot.photos()
                await bot.send_message(message.chat.id, str1)
        else:
            await bot.send_message(message.chat.id, "Неверная команда!")
    else:
        await message.reply("Тебе доступ запрешен, но теперь мы о тебе знаем, что ты сюда заходил)")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)