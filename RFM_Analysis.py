import pandas as pd
import numpy as np
import datetime as dt
pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.2f' % x)

data_frame = pd.read_excel("online_retail_II.xlsx")
df = data_frame.copy()

df.head()

# InvoiceNo: Fatura numarası. Her işleme yani faturaya ait eşsiz numara. C ile başlıyorsa iptal edilen işlem.
# StockCode: Ürün kodu. Her bir ürün için eşsiz numara.
# Description: Ürün ismi
# Quantity: Ürün adedi. Faturalardaki ürünlerden kaçar tane satıldığını ifade etmektedir.
# InvoiceDate: Fatura tarihi ve zamanı.
# UnitPrice: Ürün fiyatı (Sterlin cinsinden)
# CustomerID: Eşsiz müşteri numarası
# Country: Ülke ismi. Müşterinin yaşadığı ülke.

df.shape
# Toplam Ödenen Miktarı Bulduk
df["Total_Price"] = df["Quantity"] * df["Price"]
df.head()
# Boş değer var mı yok mu varsa kaç tane var
df.isnull().any()
df.isnull().sum()
# Boş değerleri attık
df.dropna(inplace = True)
df.isnull().any()
# İade alınanlar başlarında c harfi ile belirtilmiş iadeleri çıkarttık
df = df[~df["Invoice"].str.contains("C", na=False)]
df.shape

# Today date belirlemek için son transaciton tarih ve saatine bakıp belirleme yaptık
df["InvoiceDate"].max()
today_date = dt.datetime(2010, 12, 11)

# RFM metriklerini hesapladık
RFM = df.groupby("Customer ID").agg({"InvoiceDate": lambda InvoiceDate: (today_date - InvoiceDate.max()).days,
                                     "Invoice": lambda Invoice: Invoice.nunique(),
                                     "Total_Price": lambda Total_Price: Total_Price.sum()
                                     })
# Kolonları yeniden isimlendirdik
RFM.head()
RFM.columns = ["Recency", "Frequency", "Monetary"]
# Çeyrek aralıklardaki dağılımları gözlemledik
RFM.describe().T
# Monetary değerleri içerisindeki 0 olan değerleri çıkarttık
RFM = RFM[RFM["Monetary"] > 0]
# Tekrar describe atıp değişimleri gözlemliyoruz
RFM.describe().T

# RFM Skorlarını ayrı ayrı hesaplıyoruz
RFM["Recency_Score"] = pd.qcut(RFM["Recency"], 5, labels=[5, 4, 3, 2, 1])
RFM["Frequency_Score"] = pd.qcut(RFM["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5])
RFM["Monetary_Score"] = pd.qcut(RFM["Monetary"], 5, labels=[1, 2, 3, 4, 5])

# RFM skorlarını birleştiriyoruz
RFM["RFM_SCORE"] = (RFM["Recency_Score"].astype(str) + RFM["Frequency_Score"].astype(str))

# Creating & Analysing RFM Segments

seg_map = {
    r'[1-2][1-2]': 'hibernating',
    r'[1-2][3-4]': 'at_Risk',
    r'[1-2]5': 'cant_loose',
    r'3[1-2]': 'about_to_sleep',
    r'33': 'need_attention',
    r'[3-4][4-5]': 'loyal_customers',
    r'41': 'promising',
    r'51': 'new_customers',
    r'[4-5][2-3]': 'potential_loyalists',
    r'5[4-5]': 'champions'
}

RFM["Segment"] = RFM['RFM_SCORE'].replace(seg_map, regex=True)
RFM[["Segment", "Recency", "Frequency", "Monetary"]].groupby("Segment").agg({"mean", "count"})

# İlgilenilmesi gereken müşteriler
RFM[RFM["Segment"] == "need_attention"]

df_attention = pd.DataFrame()
df_attention["New_Customer_ID"] = RFM[RFM["Segment"] == "need_attention"].index
df_attention.head()
df_attention.shape

df_attention.to_csv("Need_Attention.csv")