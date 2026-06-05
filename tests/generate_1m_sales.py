import csv
import random
import uuid
from datetime import datetime, timedelta

# Categorias e 10 produtos para cada
catalog = {
    "Eletrônicos": [
        "Smartphone X", "Notebook Pro", "Monitor 4K", "Teclado Mecânico", "Mouse Sem Fio",
        "Tablet 10", "Smart TV 55", "Fone Bluetooth", "Câmera Mirrorless", "Console de Videogame"
    ],
    "Móveis": [
        "Cadeira Gamer", "Mesa de Escritório", "Sofá 3 Lugares", "Estante de Livros", "Cama Queen",
        "Guarda-Roupa", "Mesa de Jantar", "Cadeira de Jantar", "Rack de TV", "Criado-Mudo"
    ],
    "Vestuário": [
        "Camiseta Básica", "Calça Jeans", "Tênis Esportivo", "Jaqueta de Couro", "Vestido de Verão",
        "Moletom com Capuz", "Bermuda Cargo", "Camisa Social", "Saia Midi", "Bota de Inverno"
    ],
    "Alimentos": [
        "Café Especial 500g", "Azeite de Oliva Extra Virgem", "Chocolate Amargo 70%", "Vinho Tinto Reserva", "Queijo Parmesão",
        "Arroz Basmati", "Massa Artesanal", "Molho de Tomate Orgânico", "Castanha de Caju", "Mel Puro"
    ],
    "Beleza e Perfumaria": [
        "Perfume Importado", "Creme Hidratante", "Protetor Solar", "Shampoo Premium", "Condicionador Reconstrutor",
        "Sérum Facial", "Batom Matte", "Máscara de Cílios", "Base Líquida", "Demaquilante"
    ]
}

# Preços base simulados
base_prices = {}
for category, products in catalog.items():
    for prod in products:
        if category == "Eletrônicos": base_prices[prod] = round(random.uniform(150.0, 5000.0), 2)
        elif category == "Móveis": base_prices[prod] = round(random.uniform(100.0, 2000.0), 2)
        elif category == "Vestuário": base_prices[prod] = round(random.uniform(30.0, 300.0), 2)
        elif category == "Alimentos": base_prices[prod] = round(random.uniform(10.0, 150.0), 2)
        elif category == "Beleza e Perfumaria": base_prices[prod] = round(random.uniform(20.0, 400.0), 2)

categories = list(catalog.keys())
start_date = datetime.today() - timedelta(days=2*365) # 2 years ago

def random_date(start, days=730):
    return start + timedelta(seconds=random.randint(0, days * 24 * 60 * 60))

import os
filename = os.path.join(os.path.dirname(__file__), "datasets/vendas_1M.csv")

print(f"Gerando 1 milhão de linhas em {filename}...")

with open(filename, mode="w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # Nomenclatura das 7 colunas o mais próximo do real
    writer.writerow([
        "id_transacao", 
        "data_venda", 
        "categoria_produto", 
        "nome_produto", 
        "quantidade", 
        "preco_unitario", 
        "valor_total_venda"
    ])
    
    for i in range(1000000):
        cat = random.choice(categories)
        prod = random.choice(catalog[cat])
        qty = random.randint(1, 10)
        price = base_prices[prod]
        
        # Simula variação de preço
        discount = random.uniform(0.8, 1.0)
        final_price = round(price * discount, 2)
        total = round(final_price * qty, 2)
        
        dt = random_date(start_date)
        
        writer.writerow([
            str(uuid.uuid4())[:8], # short ID
            dt.strftime("%Y-%m-%d %H:%M:%S"),
            cat,
            prod,
            qty,
            final_price,
            total
        ])
        
print("Arquivo gerado com sucesso!")
