#!/usr/bin/env python3
"""Render a dated, manually verified selection from the operational menu.

Prices below were read in the public Live Menu UI on 19 October 2026.
This is a selection, not an assertion that the operational catalogue is static.
"""
import html
import json
import re

SOURCE = 'https://livemenu.app/menu/61cb5857aa455a0012ebbdcf'
VERIFIED_ON = '2026-10-19'
LANGS = ('pt', 'en', 'es')
# Names and short descriptions are localized; BRL prices and portions are shared.
ITEMS = {
    'cafe-da-manha': [
        (('Café da Embaixada para 2', 'Embaixada breakfast for 2', 'Desayuno Embaixada para 2'),
         ('Pães de fermentação natural, frios, iogurte, granola, manteiga, geleia, mel, fruta, bolo, mini açaí e pão de queijo.',
          'Sourdough breads, cold cuts, yogurt, granola, butter, jam, honey, fruit, cake, mini açaí and cheese bread.',
          'Panes de masa madre, fiambres, yogur, granola, mantequilla, mermelada, miel, fruta, pastel, mini açaí y pan de queso.'), '98,70'),
    ],
    'almoco': [
        (('Feijoada da Academia da Cachaça — para 2', 'Academia da Cachaça feijoada — for 2', 'Feijoada de Academia da Cachaça — para 2'),
         ('Servida por meio de parceria formal, com arroz, couve, farofa e laranja.',
          'Served through a formal partnership, with rice, collard greens, farofa and orange.',
          'Servida mediante una colaboración formal, con arroz, col, farofa y naranja.'), '189,70'),
        (('Picanha à Brasileira — individual', 'Brazilian picanha — individual', 'Picanha brasileña — individual'),
         ('Porção de aproximadamente 200 g, com arroz, farofa, molho à campanha e batata frita.',
          'Approximately 200 g, with rice, farofa, Brazilian vinaigrette and French fries.',
          'Aproximadamente 200 g, con arroz, farofa, vinagreta brasileña y papas fritas.'), '134,70'),
        (('Picanha à Brasileira — para 2', 'Brazilian picanha — for 2', 'Picanha brasileña — para 2'),
         ('Porção de aproximadamente 400 g, com arroz, farofa, molho à campanha e batata frita.',
          'Approximately 400 g, with rice, farofa, Brazilian vinaigrette and French fries.',
          'Aproximadamente 400 g, con arroz, farofa, vinagreta brasileña y papas fritas.'), '204,70'),
        (('Picadinho Carioca de Mignon', 'Carioca filet mignon picadinho', 'Picadinho carioca de filet mignon'),
         ('Mignon com molho especial, arroz branco, ovo, farofa e banana frita.',
          'Filet mignon with house sauce, white rice, egg, farofa and fried banana.',
          'Filet mignon con salsa de la casa, arroz blanco, huevo, farofa y banana frita.'), '74,70'),
        (('Salmão com molho de maracujá', 'Salmon with passion fruit sauce', 'Salmón con salsa de maracuyá'),
         ('Arroz de brócolis e legumes da estação grelhados.',
          'Broccoli rice and grilled seasonal vegetables.',
          'Arroz con brócoli y verduras de temporada a la parrilla.'), '114,70'),
    ],
    'petiscos': [
        (('Pastelzinho de queijo Minas padrão', 'Minas cheese mini pastries', 'Mini empanadas de queso Minas'),
         ('4 unidades, com mel de pimenta à parte.', '4 pieces, with chilli honey on the side.', '4 unidades, con miel picante aparte.'), '45,70'),
        (('Pastelzinho de carne', 'Beef mini pastries', 'Mini empanadas de carne'),
         ('4 unidades, com molho à campanha à parte.', '4 pieces, with Brazilian vinaigrette on the side.', '4 unidades, con vinagreta brasileña aparte.'), '48,70'),
        (('Bolinho de bacalhau', 'Salt cod fritters', 'Buñuelos de bacalao'),
         ('Porção com 10 unidades.', '10 pieces per serving.', 'Porción de 10 unidades.'), '74,70'),
        (('Aipim frito', 'Fried cassava', 'Yuca frita'),
         ('Com queijo parmesão.', 'With Parmesan cheese.', 'Con queso parmesano.'), '44,70'),
    ],
    'drinks': [
        (('Caipirinha Da Casa', 'Da Casa caipirinha', 'Caipirinha Da Casa'),
         ('Cachaça envelhecida, gengibre, bitter de ervas e limões siciliano e tahiti.',
          'Aged cachaça, ginger, herbal bitters, lemon and lime.',
          'Cachaça añejada, jengibre, bitter de hierbas, limón y lima.'), '42,00'),
        (('Chope Heineken — tulipa', 'Heineken draft beer — tulip glass', 'Cerveza Heineken de barril — copa tulipa'),
         ('Servido na tulipa.', 'Served in a tulip glass.', 'Servida en copa tulipa.'), '18,00'),
        (('Chope Heineken — caneca', 'Heineken draft beer — mug', 'Cerveza Heineken de barril — jarra'),
         ('Servido na caneca.', 'Served in a mug.', 'Servida en jarra.'), '27,00'),
        (('Água de coco', 'Coconut water', 'Agua de coco'),
         ('Unidade.', 'One coconut.', 'Unidad.'), '16,00'),
    ],
}
# Additional items verified in the same UI session; retain useful long-tail menu
# content without carrying the unverified October 2025 catalogue forward.
MORE_ITEMS = [
    (('Mais entradas', 'More starters', 'Más entradas'), [
        (('Pastelzinho de carne seca com Catupiry — 4 unidades', 'Dried beef and Catupiry mini pastries — 4 pieces', 'Mini empanadas de carne seca y Catupiry — 4 unidades'), '48,70'),
        (('Pastelzinho de camarão com Catupiry — 4 unidades', 'Shrimp and Catupiry mini pastries — 4 pieces', 'Mini empanadas de camarón y Catupiry — 4 unidades'), '49,70'),
        (('Espetinho de filé mignon — 2 unidades', 'Filet mignon skewers — 2 pieces', 'Brochetas de filet mignon — 2 unidades'), '58,70'),
        (('Espetinho de frango com bacon — 2 unidades', 'Chicken and bacon skewers — 2 pieces', 'Brochetas de pollo con bacon — 2 unidades'), '39,70'),
        (('Espetinhos de camarão — 2 unidades', 'Shrimp skewers — 2 pieces', 'Brochetas de camarón — 2 unidades'), '49,70'),
        (('Espetinhos de queijo coalho — 2 unidades', 'Coalho cheese skewers — 2 pieces', 'Brochetas de queso coalho — 2 unidades'), '27,70'),
        (('Espetinhos de abobrinha — 2 unidades', 'Zucchini skewers — 2 pieces', 'Brochetas de calabacín — 2 unidades'), '19,70'),
        (('Batata frita com cheddar e bacon', 'French fries with cheddar and bacon', 'Papas fritas con cheddar y bacon'), '49,70'),
        (('Gurjão de peixe com molho tártaro', 'Fish strips with tartar sauce', 'Tiras de pescado con salsa tártara'), '74,70'),
        (('Filé mignon aperitivo', 'Filet mignon appetizer', 'Aperitivo de filet mignon'), '89,70'),
    ]),
    (('Hambúrgueres e sanduíches', 'Burgers and sandwiches', 'Hamburguesas y sándwiches'), [
        (('Cheeseburguer Clássico de picanha', 'Classic picanha cheeseburger', 'Hamburguesa clásica de picanha con queso'), '52,70'),
        (('Hambúrguer de picanha Cheddar & Bacon', 'Cheddar & Bacon picanha burger', 'Hamburguesa de picanha Cheddar & Bacon'), '57,70'),
        (('Embaixador — dois hambúrgueres de picanha', 'Embaixador — double picanha burger', 'Embaixador — hamburguesa doble de picanha'), '67,70'),
        (('Sanduíche de filé mignon com queijo', 'Filet mignon and cheese sandwich', 'Sándwich de filet mignon con queso'), '57,70'),
        (('Pão com linguiça artesanal', 'Artisan sausage sandwich', 'Sándwich de salchicha artesanal'), '48,70'),
        (('Sanduíche de frango com mostarda e mel', 'Honey mustard chicken sandwich', 'Sándwich de pollo con mostaza y miel'), '44,70'),
    ]),
    (('Saladas e pratos individuais', 'Salads and individual dishes', 'Ensaladas y platos individuales'), [
        (('Salada Caesar com frango grelhado', 'Caesar salad with grilled chicken', 'Ensalada César con pollo a la parrilla'), '54,70'),
        (('Risoto de quinoa com vegetais e shitake', 'Quinoa risotto with vegetables and shiitake', 'Risotto de quinoa con verduras y shiitake'), '64,70'),
        (('Carioquinha de peixe', 'Carioquinha grilled fish plate', 'Carioquinha de pescado'), '64,70'),
        (('Carioquinha de frango', 'Carioquinha grilled chicken plate', 'Carioquinha de pollo'), '54,70'),
        (('Carioquinha de filé mignon', 'Carioquinha filet mignon plate', 'Carioquinha de filet mignon'), '69,70'),
    ]),
    (('Menu infantil — até 10 anos', 'Children’s menu — up to age 10', 'Menú infantil — hasta 10 años'), [
        (('Filé mignon infantil', 'Children’s filet mignon', 'Filet mignon infantil'), '59,70'),
        (('Filé de frango infantil', 'Children’s chicken fillet', 'Filete de pollo infantil'), '49,70'),
        (('Macarrão à bolonhesa infantil', 'Children’s spaghetti Bolognese', 'Espaguetis a la boloñesa infantiles'), '49,70'),
    ]),
    (('Opções do café da manhã', 'Breakfast options', 'Opciones de desayuno'), [
        (('Omelete de queijo prato e presunto', 'Ham and cheese omelette', 'Tortilla de queso y jamón'), '29,00'),
        (('Omelete de queijo Minas e tomate', 'Minas cheese and tomato omelette', 'Tortilla de queso Minas y tomate'), '32,00'),
        (('Omelete de shitake fresco', 'Fresh shiitake omelette', 'Tortilla de shiitake fresco'), '34,00'),
        (('Ovos mexidos com bacon', 'Scrambled eggs with bacon', 'Huevos revueltos con bacon'), '23,00'),
        (('Ovos fritos', 'Fried eggs', 'Huevos fritos'), '19,00'),
        (('Misto quente', 'Toasted ham and cheese sandwich', 'Sándwich caliente de jamón y queso'), '16,00'),
        (('Queijo quente', 'Grilled cheese sandwich', 'Sándwich caliente de queso'), '16,00'),
        (('Sanduíche de peito de peru com queijo Minas', 'Turkey and Minas cheese sandwich', 'Sándwich de pavo con queso Minas'), '19,00'),
        (('Pão na chapa', 'Griddled bread', 'Pan a la plancha'), '9,00'),
        (('Seleção de pães', 'Bread selection', 'Selección de panes'), '18,00'),
    ]),
    (('Cafés e bebidas', 'Coffee and drinks', 'Cafés y bebidas'), [
        (('Espresso', 'Espresso', 'Espresso'), '7,00'),
        (('Espresso duplo', 'Double espresso', 'Espresso doble'), '10,50'),
        (('Cappuccino', 'Cappuccino', 'Capuchino'), '16,50'),
        (('Café com leite', 'Coffee with milk', 'Café con leche'), '12,50'),
        (('Mojito com Havana Club 3 años', 'Mojito with Havana Club 3 años', 'Mojito con Havana Club 3 años'), '45,00'),
        (('Aperol Spritz', 'Aperol Spritz', 'Aperol Spritz'), '42,00'),
        (('Heineken 0,0% — 330 ml', 'Heineken 0.0% — 330 ml', 'Heineken 0,0% — 330 ml'), '20,00'),
    ]),
]
COPY = {
    'pt': {
        'headings': ('Café da manhã', 'Almoço brasileiro', 'Petiscos e entradas', 'Drinks e bebidas'),
        'hours': ('Todos os dias · 08h30–11h30', 'Todos os dias · 11h30–17h', 'Todos os dias · 08h30–21h', 'Todos os dias · 08h30–21h'),
        'kicker': 'Cardápio online', 'title': 'Mais opções do cardápio',
        'intro': 'Confira mais opções verificadas no cardápio online em 19/10/2026. Para todas as porções de bobó de camarão, vinhos, espumantes e demais opções, consulte o menu completo.',
        'note': 'Valores em reais. Preços, porções e disponibilidade podem mudar; confirme no cardápio online e com a equipe antes do pedido. A reserva da mesa não inclui o ingresso do Parque Bondinho.',
        'link': 'Abrir cardápio completo com preços', 'source': 'Fonte: cardápio online oficial da Embaixada Carioca · consulta em 19/10/2026.',
    },
    'en': {
        'headings': ('Breakfast', 'Brazilian lunch', 'Snacks and starters', 'Cocktails and drinks'),
        'hours': ('Daily · 8:30–11:30 AM', 'Daily · 11:30 AM–5:00 PM', 'Daily · 8:30 AM–9:00 PM', 'Daily · 8:30 AM–9:00 PM'),
        'kicker': 'Online menu', 'title': 'More options from the menu',
        'intro': 'Explore more options checked against the online menu on 19 October 2026. For all shrimp bobó portions, wines, sparkling wines and other options, see the full menu.',
        'note': 'Prices are in Brazilian reais. Prices, portions and availability may change; check the online menu and confirm with the team before ordering. Your table reservation does not include park admission.',
        'link': 'Open the full menu and prices', 'source': 'Source: Embaixada Carioca official online menu · checked on 19 October 2026.',
    },
    'es': {
        'headings': ('Desayuno', 'Almuerzo brasileño', 'Aperitivos y entradas', 'Cócteles y bebidas'),
        'hours': ('Todos los días · 08:30–11:30', 'Todos los días · 11:30–17:00', 'Todos los días · 08:30–21:00', 'Todos los días · 08:30–21:00'),
        'kicker': 'Menú online', 'title': 'Más opciones del menú',
        'intro': 'Descubre más opciones comprobadas en el menú online el 19/10/2026. Para todas las porciones de bobó de camarones, vinos, espumantes y otras opciones, consulta el menú completo.',
        'note': 'Precios en reales brasileños. Los precios, las porciones y la disponibilidad pueden cambiar; consulta el menú online y confirma con el equipo antes de pedir. La reserva de mesa no incluye la entrada al parque.',
        'link': 'Abrir menú completo con precios', 'source': 'Fuente: menú online oficial de Embaixada Carioca · consulta del 19/10/2026.',
    },
}


def render_section(section, lang):
    idx = LANGS.index(lang)
    number = list(ITEMS).index(section)
    copy = COPY[lang]
    cards = []
    for names, descriptions, price in ITEMS[section]:
        cards.append('<article class="menu-item"><h3 class="menu-item-name">'+html.escape(names[idx])+'</h3><p class="menu-item-desc">'+html.escape(descriptions[idx])+'</p><span class="menu-item-price">R$ '+price+'</span></article>')
    return '<section class="menu-section" id="'+section+'"><div class="wrap"><div class="menu-section-head"><span class="tag">0'+str(number+1)+'</span><h2>'+copy['headings'][number]+'</h2><span class="hours">'+copy['hours'][number]+'</span></div><div class="menu-items">'+'\n'.join(cards)+'</div></div></section>'


def refresh_menu_schema(text, lang):
    idx = LANGS.index(lang)
    url = 'https://www.embaixadacarioca.com/'+('' if lang=='pt' else lang+'/')+'cardapio.html'
    sections = []
    for number, (_, rows) in enumerate(ITEMS.items()):
        sections.append((COPY[lang]['headings'][number], [(names[idx], price) for names, _, price in rows]))
    sections.extend((names[idx], [(item[idx],price) for item,price in rows]) for names,rows in MORE_ITEMS)
    menu = {'@type':'Menu', '@id':url+'#menu', 'url':url, 'inLanguage':'pt-BR' if lang=='pt' else lang,
            'name':{'pt':'Seleção do cardápio da Embaixada Carioca', 'en':'Embaixada Carioca menu selection', 'es':'Selección del menú de Embaixada Carioca'}[lang],
            'dateModified':VERIFIED_ON, 'hasMenuSection':[]}
    for name, rows in sections:
        menu['hasMenuSection'].append({'@type':'MenuSection','name':name,'hasMenuItem':[
            {'@type':'MenuItem','name':label,'offers':{'@type':'Offer','price':price.replace(',','.'),'priceCurrency':'BRL','url':SOURCE}} for label,price in rows]})
    found = 0
    def replace(match):
        nonlocal found
        payload = json.loads(match[2])
        if '@graph' not in payload: return match[0]
        graph = payload['@graph']
        if not any(node.get('@type')=='Menu' for node in graph): return match[0]
        if found: raise ValueError('Unexpected second menu graph: '+lang)
        payload['@graph'] = [node for node in graph if node.get('@type')!='Menu']+[menu]
        found += 1
        return match[1]+json.dumps(payload,ensure_ascii=False,indent=2)+match[3]
    text = re.sub(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', replace, text, flags=re.S|re.I)
    if found!=1: raise ValueError('Menu graph missing: '+lang)
    return text


def refresh_menu(text, lang):
    for section in ITEMS:
        pattern = r'<section\b[^>]*class="menu-section"[^>]*id="'+section+r'"[^>]*>.*?</section>'
        text, count = re.subn(pattern, lambda _: render_section(section, lang), text, count=1, flags=re.S)
        if count != 1:
            raise ValueError('Menu section missing: '+lang+'/'+section)
    copy = COPY[lang]
    idx = LANGS.index(lang)
    categories = []
    for names, rows in MORE_ITEMS:
        cards = ''.join('<div class="ec-complete-item"><div class="ec-complete-name">'+html.escape(item[idx])+'</div><div class="ec-complete-price">R$ '+price+'</div></div>' for item,price in rows)
        categories.append('<article class="ec-menu-complete-section"><h3>'+html.escape(names[idx])+'</h3>'+cards+'</article>')
    online = '<section class="ec-menu-complete light-section ec-reading-section" id="cardapio-completo"><div class="wrap"><div class="kicker">'+copy['kicker']+'</div><h2>'+copy['title']+'</h2><p class="intro">'+copy['intro']+'</p><p class="ec-menu-note">'+copy['note']+'</p><a class="btn" href="'+SOURCE+'">'+copy['link']+'</a><div class="ec-menu-complete-grid">'+''.join(categories)+'</div><p class="ec-menu-source">'+copy['source']+'</p></div></section>'
    text, count = re.subn(r'<section\b[^>]*id="cardapio-completo"[^>]*>.*?</section>', lambda _:online, text, count=1, flags=re.S)
    if count != 1:
        raise ValueError('Complete menu section missing: '+lang)
    # This appended section listed desserts and prices absent from the source check.
    text = re.sub(r'<section class="section" style="background:#f8f5f0;padding:60px 0;">.*?</section>', '', text, flags=re.S)
    return refresh_menu_schema(text,lang)
