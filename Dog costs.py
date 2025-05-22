import openai
from flask import Flask, request, render_template_string
import os

# 請先設定環境變數 OPENAI_API_KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

# 保持原有犬種資料，請替換為你的完整列表，切勿更動結構
BREEDS = [
    {'breed':'吉娃娃', 'lifespan':16, 'personality':'敏感機警、神經質、自我中心'},
    {'breed':'博美犬', 'lifespan':14, 'personality':'活潑好動、聰明好訓練、好奇親人'},
    {'breed':'約克夏', 'lifespan':16, 'personality':'勇敢忠誠、機警、固執'},
    {'breed':'馬爾濟斯', 'lifespan':14, 'personality':'溫馴、親人、需定期美容'},
    {'breed':'臘腸犬', 'lifespan':14, 'personality':'好奇、頑皮、長壽'},
    {'breed':'迷你貴賓犬', 'lifespan':13, 'personality':'聰明、熱情、易訓練'},
    {'breed':'法國鬥牛犬', 'lifespan':12, 'personality':'溫和、依賴、愛玩'},
    {'breed':'比熊犬', 'lifespan':14, 'personality':'活潑、友善、愛撒嬌'},
    {'breed':'西施犬', 'lifespan':13, 'personality':'溫順、親人、好相處'},
    {'breed':'迷你雪納瑞', 'lifespan':13, 'personality':'警覺、勇敢、固執'},
    {'breed':'狐狸犬', 'lifespan':13, 'personality':'活潑、聰明、忠誠'},
    {'breed':'巴哥犬', 'lifespan':13, 'personality':'愛玩、黏人、友善'},
    {'breed':'西高地白梗', 'lifespan':14, 'personality':'活潑、好奇、勇敢'},
    {'breed':'柴犬', 'lifespan':14, 'personality':'忠誠、獨立、警覺'},
    {'breed':'柯基', 'lifespan':14, 'personality':'聰明、活潑、友善'},
    {'breed':'拉不拉多', 'lifespan':11, 'personality':'友善、忠實、活潑'},
    {'breed':'黃金獵犬', 'lifespan':11, 'personality':'溫和、親人、聰明'},
    {'breed':'哈士奇', 'lifespan':13, 'personality':'活力充沛、友善、頑皮'},
    {'breed':'邊境牧羊犬', 'lifespan':14, 'personality':'聰明、活潑熱情、忠誠'},
    {'breed':'杜賓犬', 'lifespan':11, 'personality':'警覺、忠誠、警戒性高'},
    {'breed':'大丹犬', 'lifespan':8,  'personality':'溫馴、溫和、親人'},
    {'breed':'薩摩耶', 'lifespan':13, 'personality':'溫和、忠誠、充滿活力'},
    {'breed':'古代牧羊犬', 'lifespan':11, 'personality':'忠實、友善、親切'},
    {'breed':'秋田犬', 'lifespan':11, 'personality':'獨立自主、沉穩、忠實'}
]
ANNUAL_MIN = 30000
ANNUAL_MAX = 60000

app = Flask(__name__)

# HTML 範本，移除本地圖片路徑，改用 {{ result.image_url }}
HTML_TEMPLATE = '''<!doctype html>
<html lang="zh-TW">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>🐶 狗狗飼養成本查詢</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body { background: #f8f9fa; }
    .card-img-top { height: 250px; object-fit: cover; }
  </style>
</head>
<body>
  <nav class="navbar navbar-dark bg-primary mb-4">
    <div class="container-fluid">
      <span class="navbar-brand mb-0 h1">🐾 狗狗小檔案查詢</span>
    </div>
  </nav>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <form method="post">
          <div class="input-group mb-4">
            <input name="breed" type="text" class="form-control" placeholder="輸入犬種名稱，例如：柴犬">
            <button class="btn btn-primary" type="submit">查詢</button>
          </div>
        </form>
        {% if result %}
        <div class="card">
          <img src="{{ result.image_url }}" class="card-img-top" alt="Dog">
          <div class="card-body text-center">
            <h5 class="card-title">{{ result.breed }}</h5>
            <p class="card-text">平均壽命：{{ result.lifespan }} 年</p>
            <p class="card-text">花費預估： {{ annual_min }}~{{ annual_max }} 元/年；總計 {{ total_min }}~{{ total_max }} 元</p>
            <p class="card-text">個性/特性：{{ result.personality }}</p>
          </div>
        </div>
        {% elif error %}
        <div class="alert alert-warning" role="alert">
          {{ error }}
        </div>
        {% endif %}
      </div>
    </div>
  </div>
</body>
</html>'''

def generate_dog_image(breed: str) -> str:
    """使用 OpenAI Image API 生成指定犬種的照片，回傳圖片 URL"""
    try:
        resp = openai.Image.create(
            prompt=f"High quality photo of a {breed} dog, realistic photography",
            n=1,
            size="512x512"
        )
        return resp['data'][0]['url']
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    error = None
    total_min = total_max = annual_min = ANNUAL_MIN
    annual_max = ANNUAL_MAX
    if request.method == 'POST':
        breed = request.form.get('breed')
        data = next((b for b in BREEDS if b['breed'] == breed), None)
        if not data:
            error = '找不到相關犬種資料，請確認名稱是否正確。'
        else:
            img_url = generate_dog_image(breed)
            if not img_url:
                error = '圖片生成失敗，請稍後再試。'
            result = data.copy()
            result['image_url'] = img_url
            total_min = data['lifespan'] * ANNUAL_MIN
            total_max = data['lifespan'] * ANNUAL_MAX
    return render_template_string(HTML_TEMPLATE,
                                  result=result,
                                  error=error,
                                  annual_min=ANNUAL_MIN,
                                  annual_max=ANNUAL_MAX,
                                  total_min=total_min,
                                  total_max=total_max)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)), debug=True)
