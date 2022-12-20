# def get_current_show(station_name):
#     splat = file_name.split(".")[0].split("_")
#     print(f'Checkpoint line 125 of colour.py. What we want to split comes to {splat}')
#     timestamp = splat[1]
#     station_name = splat[0].split("/")[1].lower()
#     show, dj = '', ''

#     try:
#         show_deets = get_current_show(station_name)
#         show, dj = show_deets[0], show_deets[1]
#     except Exception as e:
#         print(e)

#     utc_now = datetime.utcnow()
#     utc_now_day = utc_now.strftime('%w')
#     utc_now_hour = utc_now.hour

#     # select statement where day is the same and hour is same as or equal to begin and less than end (this select statement could be improved upon over time)
#     conn = psycopg2.connect('postgresql://postgres:BBWjnHbbic4d0qoJnQYe@containers-us-west-46.railway.app:7052/railway')
#     cursor = conn.cursor()

#     cursor.execute('SELECT show, dj FROM schedules WHERE station = (%s) AND begin_day = (%s) AND begin_hour <= (%s) AND end_hour > (%s)',
#                    (station_name, utc_now_day, utc_now_hour, utc_now_hour))

#     shows = cursor.fetchall()
#     conn.commit()
#     cursor.close()
#     conn.close()

#     if len(shows) == 1:
#         return shows[0]
#     else:
#         print('problem here!')
#         return

# def get_chroma_range(max, min, initial):
#     percentile = (initial - min) / (max - min)
#     if percentile > 1:
#         return .95
#     if percentile < 0:
#         return .05
#     return percentile

    # RGB
    # [r, g, b] = hsluv.hsluv_to_rgb(
    #     [(tempo_percentile / 100) * 180 + 180, loudness_percentile, pitch_percentile])
    # rgb = round(r * 255), round(g * 255), round(b * 255)

    # def lab_to_rgb(l, a, b):
    # def to_rgb(color):
    #     color = round(color * 255)
    #     if color > 255:
    #         return 255
    #     if color < 0:
    #         return 0
    #     return color

    # color1_lab = LabColor(l, a, b)
    # print(color1_lab)

    # color1_rgb = convert_color(color1_lab, sRGBColor)
    # color1_rgb_tuple = color1_rgb.get_value_tuple()
    # print(color1_rgb_tuple)
    # r, g, b = to_rgb(color1_rgb_tuple[0]), to_rgb(
    #     color1_rgb_tuple[1]), to_rgb(color1_rgb_tuple[2])

    # return [r, g, b]

# import hsluv
# from sty import bg
     # qui = bg(r, g, b) + \
    #     "                " + bg.rs
    # print(qui)

# SOMA URLS

# 'SOMADSO': 'https://ice6.somafm.com/deepspaceone-128-mp3',
# 'SOMADESI': 'https://ice1.somafm.com/suburbsofgoa-128-mp3',
# 'SOMAMTL': 'https://ice1.somafm.com/metal-128-mp3',
# 'SOMACLQ': 'https://ice6.somafm.com/cliqhop-128-mp3',
# 'SOMAFOLK': 'https://ice4.somafm.com/folkfwd-128-mp3',
# 'SOMALUSH': 'https://ice1.somafm.com/lush-128-mp3',
# 'SOMAPOPT': 'https://ice1.somafm.com/poptron-128-mp3',
# 'SOMAVPR': 'https://ice2.somafm.com/vaporwaves-128-mp3',
# 'SOMAIND': 'https://ice4.somafm.com/indiepop-128-mp3',