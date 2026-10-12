#!/usr/bin/env python3
"""Surgical, repeatable P1/P2 editorial changes; --check never writes."""
import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = 'https://www.embaixadacarioca.com'
# Each group is an intent, with PT/EN/ES equivalents kept together.
# file, title, description, H1, opening paragraph
GROUPS = {
 'menu': [
  ('cardapio.html', 'Cardápio e Preços | Embaixada Carioca no Morro da Urca', 'Consulte o cardápio da Embaixada Carioca: café da manhã, picanha, feijoada, petiscos e drinks. Menu online com preços e opções no Morro da Urca.', 'Cardápio da Embaixada Carioca', 'Explore café da manhã, almoço brasileiro, petiscos e drinks no Morro da Urca. Consulte preços, opções e disponibilidade no cardápio online atualizado.'),
  ('en/cardapio.html', 'Menu & Prices | Embaixada Carioca at Urca Hill', 'Browse breakfast, Brazilian lunch, picanha, feijoada and drinks at Embaixada Carioca. See current prices in the online menu before visiting Urca Hill.', 'Embaixada Carioca menu and prices', 'Explore breakfast, Brazilian lunch, snacks and drinks on Urca Hill. Check current prices, options and availability in the online menu.'),
  ('es/cardapio.html', 'Menú y Precios | Embaixada Carioca en Morro da Urca', 'Consulta desayunos, almuerzos, picanha, feijoada y bebidas de Embaixada Carioca. Menú online con precios actualizados antes de visitar el Morro da Urca.', 'Menú y precios de Embaixada Carioca', 'Descubre desayunos, almuerzos brasileños, aperitivos y bebidas en el Morro da Urca. Consulta precios, opciones y disponibilidad en el menú online actualizado.')],
 'breakfast': [
  ('cafe-da-manha.html', 'Café da Manhã com Vista | Embaixada Carioca, Rio', 'Café da manhã com vista para o Pão de Açúcar, no Morro da Urca, até 11h30. Veja o cardápio e reserve. Ingresso do Bondinho vendido separadamente.', 'Café da manhã com vista para o Pão de Açúcar', 'Tome café da manhã com vista direta para o Pão de Açúcar, no Morro da Urca, a 220 metros de altitude. O serviço vai até 11h30; escolha as opções no cardápio e planeje o acesso ao parque.'),
  ('en/cafe-da-manha.html', 'Breakfast with a Sugarloaf View | Embaixada Carioca', 'Breakfast with a Sugarloaf Mountain view on Urca Hill until 11:30 AM. Explore the menu and book a table. Cable-car tickets are purchased separately.', 'Breakfast with a view of Sugarloaf Mountain', 'Have breakfast facing Sugarloaf Mountain on Urca Hill, 220 meters above sea level. Breakfast is served until 11:30 AM; explore the menu and plan your park access.'),
  ('es/cafe-da-manha.html', 'Desayuno con Vista al Pan de Azúcar | Embaixada Carioca', 'Desayuna con vista al Pan de Azúcar en el Morro da Urca hasta las 11:30. Consulta el menú y reserva. La entrada del teleférico se compra por separado.', 'Desayuno con vista al Pan de Azúcar', 'Desayuna frente al Pan de Azúcar en el Morro da Urca, a 220 metros de altitud. El servicio termina a las 11:30; consulta el menú y planifica el acceso al parque.')],
 'lunch': [
  ('almoco.html', 'Almoço com Vista no Morro da Urca | Embaixada Carioca', 'Almoço com vista para o Pão de Açúcar, das 11h30 às 17h no Morro da Urca. Picanha, feijoada e cozinha brasileira. Veja o cardápio e reserve sua mesa.', 'Almoço com vista para o Pão de Açúcar', 'Almoce com vista direta para o Pão de Açúcar, no Morro da Urca, das 11h30 às 17h. A Embaixada Carioca serve cozinha brasileira, picanha e a feijoada da Academia da Cachaça por meio de parceria formal.'),
  ('en/almoco.html', 'Lunch with a Sugarloaf View | Embaixada Carioca', 'Brazilian lunch with a Sugarloaf Mountain view on Urca Hill, 11:30 AM–5:00 PM. Picanha and feijoada. Explore the menu and reserve your table.', 'Lunch with a view of Sugarloaf Mountain', 'Enjoy Brazilian lunch facing Sugarloaf Mountain on Urca Hill, from 11:30 AM to 5:00 PM. Embaixada Carioca serves picanha and Academia da Cachaça feijoada through a formal partnership.'),
  ('es/almoco.html', 'Almuerzo con Vista al Pan de Azúcar | Embaixada Carioca', 'Almuerzo brasileño con vista al Pan de Azúcar, de 11:30 a 17:00 en el Morro da Urca. Picanha y feijoada. Consulta el menú y reserva tu mesa.', 'Almuerzo con vista al Pan de Azúcar', 'Almuerza frente al Pan de Azúcar en el Morro da Urca, de 11:30 a 17:00. Embaixada Carioca sirve cocina brasileña, picanha y la feijoada de Academia da Cachaça mediante una colaboración formal.')],
 'park': [
  ('parque-bondinho.html', 'Parque Bondinho: Ingressos e Visita | Embaixada Carioca', 'Planeje a visita ao Parque Bondinho Pão de Açúcar: ingressos, acesso e pausa no Morro da Urca. Confirme horários do parque no canal oficial.', 'Parque Bondinho: ingressos e planejamento da visita', 'O Parque Bondinho Pão de Açúcar conecta a Praia Vermelha, o Morro da Urca e o Pão de Açúcar. Na primeira parada, a Embaixada Carioca serve café da manhã e almoço com vista. Confirme horários e ingressos no site oficial do parque.'),
  ('en/parque-bondinho.html', 'Sugarloaf Cable Car: Tickets & Visit | Embaixada Carioca', 'Plan your Sugarloaf cable-car visit: tickets, access and a meal on Urca Hill. Confirm park hours on the official website before visiting.', 'Sugarloaf cable car: tickets and planning your visit', 'Sugarloaf Cable Car Park connects Praia Vermelha, Urca Hill and Sugarloaf Mountain. At the first stop, Embaixada Carioca serves breakfast and lunch with a view. Confirm park hours and tickets on the official park website.'),
  ('es/parque-bondinho.html', 'Teleférico Pan de Azúcar: Entradas y Visita', 'Planifica la visita al teleférico del Pan de Azúcar: entradas, acceso y comida en el Morro da Urca. Confirma horarios en el sitio oficial del parque.', 'Teleférico del Pan de Azúcar: entradas y visita', 'El Parque Bondinho conecta Praia Vermelha, el Morro da Urca y el Pan de Azúcar. En la primera parada, Embaixada Carioca sirve desayuno y almuerzo con vista. Confirma horarios y entradas en el sitio oficial del parque.')],
 'hill': [
  ('morro-da-urca.html', 'Morro da Urca: Como Chegar, Passeio e Onde Comer', 'Visite o Morro da Urca, primeira parada do Bondinho: mirantes, acesso e pausa para café da manhã ou almoço com vista para o Pão de Açúcar.', 'Morro da Urca: passeio, vista e onde comer', 'O Morro da Urca é a primeira parada do Bondinho, a 220 metros de altitude. Planeje o acesso, aproveite os mirantes e escolha uma pausa para café da manhã ou almoço com vista para o Pão de Açúcar.'),
  ('en/morro-da-urca.html', 'Urca Hill: Getting There, Views & Food | Rio Guide', 'Visit Urca Hill, the first Sugarloaf cable-car stop: viewpoints, access and breakfast or lunch with a view of Sugarloaf Mountain.', 'Urca Hill: views, things to do and where to eat', 'Urca Hill is the first Sugarloaf cable-car stop, 220 meters above sea level. Plan your access, explore the viewpoints and stop for breakfast or lunch with a view of Sugarloaf Mountain.'),
  ('es/morro-da-urca.html', 'Morro da Urca: Cómo Llegar, Vistas y Dónde Comer', 'Visita el Morro da Urca, primera parada del teleférico: miradores, acceso y una pausa para desayunar o almorzar con vista al Pan de Azúcar.', 'Morro da Urca: paseo, vistas y dónde comer', 'El Morro da Urca es la primera parada del teleférico, a 220 metros de altitud. Planifica el acceso, recorre los miradores y haz una pausa para desayunar o almorzar con vista al Pan de Azúcar.')],
 'access': [
  ('como-chegar.html', 'Como Chegar à Embaixada Carioca | Morro da Urca', 'Entre pela Av. Pasteur, 520, e desembarque na primeira parada do Bondinho. Entenda ingresso, trilha quando aberta e acesso à Embaixada Carioca.', 'Como chegar à Embaixada Carioca no Morro da Urca', 'Para chegar de Bondinho, entre pela Av. Pasteur, 520, na Praia Vermelha, e desembarque no Morro da Urca, a primeira parada. A reserva da mesa não inclui o ingresso. A trilha é alternativa somente quando aberta.'),
  ('en/how-to-get-there.html', 'How to Get to Embaixada Carioca | Urca Hill', 'Enter at Av. Pasteur, 520 and get off at the first Sugarloaf cable-car stop. Learn about tickets, the trail when open and restaurant access.', 'How to get to Embaixada Carioca on Urca Hill', 'For cable-car access, enter at Av. Pasteur, 520 in Praia Vermelha and get off at Urca Hill, the first stop. Your table reservation does not include a ticket. The trail is an alternative only when open.'),
  ('es/como-llegar.html', 'Cómo Llegar a Embaixada Carioca | Morro da Urca', 'Entra por Av. Pasteur, 520 y baja en la primera parada del teleférico. Consulta entradas, sendero cuando esté abierto y acceso al restaurante.', 'Cómo llegar a Embaixada Carioca en el Morro da Urca', 'Para llegar en teleférico, entra por Av. Pasteur, 520 en Praia Vermelha y baja en el Morro da Urca, la primera parada. La reserva no incluye entrada. El sendero es una alternativa solo cuando está abierto.')],
 'food': [
  ('gastronomia-carioca.html', 'Gastronomia Carioca: Feijoada, Picanha e Pratos do Rio', 'Conheça a gastronomia carioca: feijoada, picanha, petiscos e caipirinha. Veja pratos da Embaixada Carioca e planeje um almoço com vista no Morro da Urca.', 'Gastronomia carioca: pratos e sabores do Rio', 'Feijoada, picanha, petiscos e caipirinha fazem parte da experiência gastronômica carioca. Conheça esses sabores e consulte o cardápio da Embaixada Carioca para escolher seu almoço no Morro da Urca.'),
  ('en/gastronomia-carioca.html', 'Rio Food Guide: Feijoada, Picanha & Brazilian Flavours', 'Discover Rio food: feijoada, picanha, Brazilian snacks and caipirinha. Explore the Embaixada Carioca menu and plan lunch with a view on Urca Hill.', 'Rio food: Brazilian dishes and local flavours', 'Feijoada, picanha, Brazilian snacks and caipirinha are part of the Rio food experience. Learn about these flavours and browse the Embaixada Carioca menu to choose your lunch on Urca Hill.'),
  ('es/gastronomia-carioca.html', 'Gastronomía Carioca: Feijoada, Picanha y Sabores de Río', 'Descubre la gastronomía carioca: feijoada, picanha, aperitivos y caipirinha. Consulta el menú de Embaixada Carioca y planifica un almuerzo con vista.', 'Gastronomía carioca: platos y sabores de Río', 'Feijoada, picanha, aperitivos y caipirinha forman parte de la experiencia gastronómica de Río. Conoce estos sabores y consulta el menú de Embaixada Carioca para elegir tu almuerzo en el Morro da Urca.')],
 'restaurant': [
  ('restaurante-morro-da-urca.html', 'Restaurante no Morro da Urca | Embaixada Carioca', 'Embaixada Carioca no Morro da Urca: cozinha brasileira, café da manhã e almoço com vista para o Pão de Açúcar. Veja o cardápio e reserve sua mesa.', 'Restaurante no Morro da Urca: Embaixada Carioca', 'A Embaixada Carioca é um restaurante de cozinha brasileira no Morro da Urca, a primeira parada do Bondinho. Café da manhã, almoço e drinks com vista direta para o Pão de Açúcar. Consulte o cardápio e planeje a reserva.'),
  ('en/restaurant-at-urca-hill.html', 'Restaurant on Urca Hill | Embaixada Carioca', 'Embaixada Carioca on Urca Hill: Brazilian food, breakfast and lunch with a Sugarloaf Mountain view. Explore the menu and reserve your table.', 'Restaurant on Urca Hill: Embaixada Carioca', 'Embaixada Carioca is a Brazilian restaurant on Urca Hill, the first cable-car stop. Enjoy breakfast, lunch and drinks with a direct Sugarloaf Mountain view. Browse the menu and plan your reservation.'),
  ('es/restaurante-morro-da-urca.html', 'Restaurante en Morro da Urca | Embaixada Carioca', 'Embaixada Carioca en el Morro da Urca: cocina brasileña, desayuno y almuerzo con vista al Pan de Azúcar. Consulta el menú y reserva tu mesa.', 'Restaurante en el Morro da Urca: Embaixada Carioca', 'Embaixada Carioca es un restaurante de cocina brasileña en el Morro da Urca, la primera parada del teleférico. Desayuno, almuerzo y bebidas con vista directa al Pan de Azúcar. Consulta el menú y planifica tu reserva.')],
 'cable_restaurant': [
  ('restaurante-bondinho-pao-de-acucar.html', 'Restaurante no Bondinho | Embaixada Carioca', 'Faça uma pausa na primeira parada do Bondinho: café da manhã e almoço na Embaixada Carioca. Veja o cardápio. Reserva e ingresso são separados.', 'Restaurante na primeira parada do Bondinho', 'A Embaixada Carioca fica no Morro da Urca, a primeira parada do Bondinho, antes de seguir ao Pão de Açúcar. Planeje café da manhã ou almoço durante o passeio. A reserva do restaurante e o ingresso do parque são separados.'),
  ('en/sugarloaf-cable-car-restaurant.html', 'Sugarloaf Cable Car Restaurant | Embaixada Carioca', 'Stop for breakfast or lunch at the first Sugarloaf cable-car stop on Urca Hill. Browse the menu. Restaurant reservations and park tickets are separate.', 'Restaurant at the first Sugarloaf cable-car stop', 'Embaixada Carioca is on Urca Hill, the first cable-car stop before Sugarloaf Mountain. Plan breakfast or lunch during your visit. Restaurant reservations and park tickets are separate.'),
  ('es/restaurante-bondinho-pan-de-azucar.html', 'Restaurante del Teleférico | Embaixada Carioca', 'Desayuna o almuerza en la primera parada del teleférico del Pan de Azúcar. Consulta el menú. La reserva del restaurante y la entrada son separadas.', 'Restaurante en la primera parada del teleférico', 'Embaixada Carioca está en el Morro da Urca, la primera parada del teleférico antes del Pan de Azúcar. Planifica desayuno o almuerzo durante el paseo. La reserva y la entrada al parque son separadas.')],
 'where': [
  ('onde-comer-no-pao-de-acucar.html', 'Onde Comer no Pão de Açúcar | Café e Almoço com Vista', 'Escolha onde comer durante a visita ao Pão de Açúcar: café da manhã ou almoço no Morro da Urca. Cardápio, reserva e acesso à Embaixada Carioca.', 'Onde comer durante a visita ao Pão de Açúcar', 'Se você procura onde comer durante o passeio ao Pão de Açúcar, a Embaixada Carioca fica no Morro da Urca, primeira parada do Bondinho. Compare os momentos: café da manhã até 11h30 ou almoço das 11h30 às 17h.'),
  ('en/where-to-eat-near-sugarloaf.html', 'Where to Eat at Sugarloaf | Breakfast & Lunch Guide', 'Choose where to eat during your Sugarloaf visit: breakfast or lunch on Urca Hill. Explore the Embaixada Carioca menu, reservations and park access.', 'Where to eat during your Sugarloaf visit', 'For a meal during your Sugarloaf visit, Embaixada Carioca is on Urca Hill at the first cable-car stop. Choose breakfast until 11:30 AM or Brazilian lunch from 11:30 AM to 5:00 PM.'),
  ('es/donde-comer-cerca-del-pan-de-azucar.html', 'Dónde Comer en el Pan de Azúcar | Desayuno y Almuerzo', 'Elige dónde comer durante tu visita al Pan de Azúcar: desayuno o almuerzo en el Morro da Urca. Consulta menú, reservas y acceso a Embaixada Carioca.', 'Dónde comer durante la visita al Pan de Azúcar', 'Para comer durante el paseo al Pan de Azúcar, Embaixada Carioca está en el Morro da Urca, primera parada del teleférico. Elige desayuno hasta las 11:30 o almuerzo brasileño de 11:30 a 17:00.')],
 'itinerary': [
  ('roteiro-meio-dia-urca-pao-de-acucar.html', 'Roteiro de Meio Dia: Urca, Bondinho e Almoço com Vista', 'Planeje meio dia na Urca: Praia Vermelha, Bondinho, mirantes e almoço com vista no Morro da Urca. Entenda acesso, reserva e horários do restaurante.', 'Roteiro de meio dia na Urca e no Pão de Açúcar', None),
  ('en/roteiro-meio-dia-urca-pao-de-acucar.html', 'Half-Day Urca & Sugarloaf Itinerary with Lunch', 'Plan half a day in Urca: Praia Vermelha, cable car, viewpoints and lunch with a view. Learn about park access, reservations and restaurant hours.', 'Half-day Urca and Sugarloaf itinerary', None),
  ('es/roteiro-meio-dia-urca-pao-de-acucar.html', 'Itinerario de Medio Día: Urca, Pan de Azúcar y Almuerzo', 'Planifica medio día en Urca: Praia Vermelha, teleférico, miradores y almuerzo con vista. Consulta acceso, reserva y horarios del restaurante.', 'Itinerario de medio día en Urca y el Pan de Azúcar', None)],
 'visit': [
  ('planeje-sua-visita.html', 'Planeje sua Visita ao Morro da Urca | Embaixada Carioca', 'Planeje café da manhã ou almoço com vista: acesso ao Morro da Urca, ingresso do Bondinho, cardápio e reserva da Embaixada Carioca.', None, None),
  ('en/plan-your-visit.html', 'Plan Your Sugarloaf Visit & Meal | Embaixada Carioca', 'Plan breakfast or lunch with a view: Urca Hill access, Sugarloaf cable-car tickets, the Embaixada Carioca menu and table reservations.', None, None),
  ('es/planifica-tu-visita.html', 'Planifica tu Visita al Pan de Azúcar | Embaixada Carioca', 'Planifica desayuno o almuerzo con vista: acceso al Morro da Urca, entradas del teleférico, menú y reserva en Embaixada Carioca.', None, None)],
}

EXTRAS = [
 ('en/restaurant-at-sugarloaf.html', 'Restaurant at Sugarloaf Mountain | Embaixada Carioca', 'Eat with a Sugarloaf Mountain view at Embaixada Carioca on Urca Hill, the first cable-car stop. Breakfast, Brazilian lunch and table reservations.', 'Restaurant at Sugarloaf: Embaixada Carioca on Urca Hill', 'Embaixada Carioca is on Urca Hill, the first cable-car stop inside Sugarloaf Cable Car Park. Enjoy Brazilian food with a direct view of Sugarloaf Mountain. The restaurant is not at the summit.'),
 ('restaurante-pao-de-acucar.html', 'Restaurante no Pão de Açúcar | Embaixada Carioca', 'Conheça a Embaixada Carioca no Morro da Urca, primeira parada do Bondinho. Café da manhã e almoço com vista para o Pão de Açúcar. Veja como reservar.', 'Restaurante no Pão de Açúcar: primeira parada, Morro da Urca', 'A Embaixada Carioca fica no Morro da Urca, a primeira parada do Bondinho, com o Pão de Açúcar de frente. Consulte café da manhã, almoço brasileiro e reservas. O restaurante não fica no cume do Pão de Açúcar.'),
 ('es/restaurante-pan-de-azucar.html', 'Restaurante en el Pan de Azúcar | Embaixada Carioca', 'Conoce Embaixada Carioca en el Morro da Urca, primera parada del teleférico. Desayuno y almuerzo con vista al Pan de Azúcar. Consulta menú y reservas.', 'Restaurante en el Pan de Azúcar: primera parada, Morro da Urca', 'Embaixada Carioca está en el Morro da Urca, la primera parada del teleférico, frente al Pan de Azúcar. Consulta desayuno, almuerzo brasileño y reservas. El restaurante no está en la cima del Pan de Azúcar.')]

JSONLD = re.compile(r'(<script\b[^>]*type=["\']application/ld\+json["\'][^>]*>)(.*?)(</script>)', re.I | re.S)
LOCALES = ('pt', 'en', 'es')
LINK_LABELS = {
 'pt': {'visit':'Planeje sua visita', 'breakfast':'Café da manhã com vista', 'lunch':'Almoço com vista', 'menu':'Cardápio e preços', 'access':'Como chegar', 'itinerary':'Roteiro de meio dia', 'restaurant':'Restaurante no Morro da Urca', 'where':'Onde comer no passeio'},
 'en': {'visit':'Plan your visit', 'breakfast':'Breakfast with a view', 'lunch':'Lunch with a view', 'menu':'Menu and prices', 'access':'How to get there', 'itinerary':'Half-day itinerary', 'restaurant':'Restaurant on Urca Hill', 'where':'Where to eat on your visit'},
 'es': {'visit':'Planifica tu visita', 'breakfast':'Desayuno con vista', 'lunch':'Almuerzo con vista', 'menu':'Menú y precios', 'access':'Cómo llegar', 'itinerary':'Itinerario de medio día', 'restaurant':'Restaurante en el Morro da Urca', 'where':'Dónde comer durante el paseo'},
}
RELATED = {
 'menu': ('breakfast','lunch','visit'), 'breakfast':('menu','visit','access'),
 'lunch':('menu','visit','access'), 'park':('visit','access','itinerary'),
 'hill':('visit','itinerary','where'), 'access':('visit','itinerary','restaurant'),
 'food':('menu','lunch','visit'), 'restaurant':('menu','visit','where'),
 'cable_restaurant':('visit','where','itinerary'), 'where':('breakfast','lunch','visit'),
 'itinerary':('visit','breakfast','lunch'), 'visit':('itinerary','menu','access'),
 'extra':('restaurant','where','visit')}

def locale(path):
    return 'en' if path.startswith('en/') else 'es' if path.startswith('es/') else 'pt'

def set_meta(text, title, description):
    text = re.sub(r'(<title>).*?(</title>)', lambda m:m[1]+html.escape(title)+m[2],text,count=1,flags=re.S)
    def replace(m):
        tag=m[0]
        if re.search(r'(?:name|property)=["\'](?:description|og:description|twitter:description)["\']',tag,re.I):
            return re.sub(r'content=(["\']).*?\1',lambda _: 'content="'+html.escape(description,quote=True)+'"',tag,flags=re.S)
        if re.search(r'(?:name|property)=["\'](?:og:title|twitter:title)["\']',tag,re.I):
            return re.sub(r'content=(["\']).*?\1',lambda _: 'content="'+html.escape(title,quote=True)+'"',tag,flags=re.S)
        return tag
    return re.sub(r'<meta\b[^>]*>', replace, text, flags=re.I)

def opening_hours(node, title, description, url):
    if isinstance(node,dict):
        t=node.get('@type',[]); types=[t] if isinstance(t,str) else t
        if any(x in types for x in ('Restaurant','LocalBusiness','FoodEstablishment')):
            node['openingHours']=['Mo-Su 08:30-21:00']
            node['openingHoursSpecification']=[{'@type':'OpeningHoursSpecification','dayOfWeek':['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'],'opens':'08:30','closes':'21:00'}]
        if 'Organization' in types and not node.get('logo'):
            node['logo']=SITE+'/assets/logo-azul.svg'
        if 'GeoCoordinates' in types and str(node.get('elevation'))=='227': node['elevation']='220'
        if 'WebPage' in types and (node.get('url')==url or str(node.get('@id','')).startswith(url+'#')):
            node['name']=title; node['description']=description
        for v in node.values(): opening_hours(v,title,description,url)
    elif isinstance(node,list):
        for v in node: opening_hours(v,title,description,url)

def synchronize_schema(text, title, desc, rel):
    url=SITE+('/' if rel=='index.html' else '/'+rel)
    def replace(m):
        raw=m[2]; payload=json.loads(raw)
        opening_hours(payload,title,desc,url)
        # Keep compact blocks compact; preserve already-pretty indentation.
        if payload==json.loads(raw): return m[0]
        return m[1]+json.dumps(payload,ensure_ascii=False,indent=2 if '\n' in raw else None,separators=None if '\n' in raw else (',',':'))+m[3]
    return JSONLD.sub(replace,text)

def facts(text, lang):
    # Operator confirmation on 12 October 2026: daily 08:30–21:00.
    text=re.sub(r'\b227 (metros|meters|metres)\b',r'220 \1',text)
    def table_row(m):
        row=m[0];cells=re.findall(r'<td[^>]*>(.*?)</td>',row,re.S)
        if len(cells)<2: return row
        name=re.sub('<[^>]*>','',cells[0])
        if re.search('Almoço|Lunch|Almuerzo',name,re.I) and ('3:30 PM' in cells[1] or '15:30' in cells[1]):
            return row.replace('<td>'+cells[1]+'</td>','<td>'+('11:30 AM–5:00 PM' if lang=='en' else '11:30–17:00')+'</td>',1)
        return row
    return re.sub(r'<tr\b[^>]*>.*?</tr>',table_row,text,flags=re.S)

def align_intent_links(text, lang):
    idx=LOCALES.index(lang)
    exact={
      'restaurante no morro da urca':'restaurant', 'restaurant at urca hill':'restaurant', 'restaurant on urca hill':'restaurant', 'restaurante en el morro da urca':'restaurant',
      'café da manhã com vista':'breakfast', 'breakfast with a view':'breakfast', 'desayuno con vista':'breakfast',
      'almoço com vista':'lunch', 'lunch with a view':'lunch', 'almuerzo con vista':'lunch',
      'roteiro de meio dia':'itinerary', 'half-day itinerary':'itinerary', 'itinerario de medio día':'itinerary',
      'planeje sua visita':'visit','plan your visit':'visit','planifica tu visita':'visit',
    }
    def rewrite(m):
        tag,copy=m[1],m[2];href=re.search(r'href=(["\'])(.*?)\1',tag,re.S)
        if not href: return m[0]
        target=html.unescape(href[2])
        if target.startswith(('https://','http://')) and not target.startswith(SITE+'/'): return m[0]
        if target.startswith(('#','mailto:','tel:','javascript:')): return m[0]
        label=' '.join(html.unescape(re.sub('<[^>]*>','',copy)).split()).lower()
        intent=exact.get(label)
        if not intent: return m[0]
        tag=tag[:href.start(2)]+'/'+GROUPS[intent][idx][0]+tag[href.end(2):]
        return tag+copy+'</a>'
    return re.sub(r'(<a\b[^>]*>)(.*?)</a>',rewrite,text,flags=re.S|re.I)

def related_block(group, lang, current):
    items=[]; idx=LOCALES.index(lang)
    for intent in RELATED[group]:
        rel=GROUPS[intent][idx][0]
        if rel==current: continue
        items.append('<a href="/'+rel+'" data-intent="'+('planejar_visita' if intent=='visit' else intent)+'" data-position="related_growth">'+LINK_LABELS[lang][intent]+'</a>')
    heading={'pt':'Planeje sua pausa no passeio','en':'Plan your food stop','es':'Planifica tu pausa durante el paseo'}[lang]
    return '<!-- growth-p1-p2:start --><nav class="ec-growth-links" aria-label="'+heading+'"><p>'+heading+'</p><div>'+''.join(items)+'</div></nav><!-- growth-p1-p2:end -->'

def transform(row, group):
    rel,title,desc,h1,lead=row; p=ROOT/rel; text=p.read_text();lang=locale(rel)
    text=set_meta(text,title,desc)
    if h1: text=re.sub(r'(<h1\b[^>]*>).*?(</h1>)',lambda m:m[1]+html.escape(h1)+m[2],text,count=1,flags=re.S)
    if lead:
        h=re.search(r'<h1\b[^>]*>.*?</h1>',text,re.S)
        after=text[h.end():]
        # Replace the hero's paragraph, leaving any menu hyperlink intact.
        para=re.search(r'(<p\b[^>]*>)(.*?)(</p>)',after,re.S)
        if not para: raise ValueError('Opening paragraph missing: '+rel)
        link=re.search(r'<a\b[^>]*href=["\']https://livemenu\.app/[^>]*>.*?</a>',para[2],re.S)
        copy=html.escape(lead)+(' '+link[0] if link else '')
        after=after[:para.start()]+para[1]+copy+para[3]+after[para.end():]
        text=text[:h.end()]+after
    text=synchronize_schema(text,title,desc,rel)
    text=facts(text,lang)
    text=align_intent_links(text,lang)
    if group in ('park','hill'):
        # Park hours are a separate authority; point to the official source.
        answer={
         'pt':'Confirme os horários e o último embarque do Parque Bondinho no site oficial bondinho.com.br. A Embaixada Carioca funciona todos os dias das 08h30 às 21h, com café da manhã até 11h30 e almoço das 11h30 às 17h.',
         'en':'Confirm park hours and the last cable-car departure on the official website, bondinho.com.br. Embaixada Carioca is open daily from 8:30 AM to 9:00 PM, with breakfast until 11:30 AM and lunch from 11:30 AM to 5:00 PM.',
         'es':'Confirma los horarios del parque y el último embarque en el sitio oficial bondinho.com.br. Embaixada Carioca abre todos los días de 8:30 a 21:00, con desayuno hasta las 11:30 y almuerzo de 11:30 a 17:00.'}[lang]
        old_park=re.compile(r'(?:8h(?:00)?\s*(?:às|a|–|-)\s*21h|8am\s*to\s*9pm|8:00\s*AM\s*to\s*9:00\s*PM)',re.I)
        def paragraph(m):
            visible=re.sub('<[^>]*>','',html.unescape(m[2]))
            if re.search('Parque Bondinho|Sugarloaf.*Park',visible,re.I) and old_park.search(visible):
                return m[1]+html.escape(answer)+m[3]
            return m[0]
        text=re.sub(r'(<p\b[^>]*>)(.*?)(</p>)',paragraph,text,flags=re.S|re.I)
        def faq(m):
            value=json.loads(m[2])
            def walk(n):
                if isinstance(n,dict):
                    if n.get('@type')=='Answer' and re.search('Parque Bondinho|Sugarloaf.*Park',n.get('text',''),re.I) and old_park.search(n.get('text','')): n['text']=answer
                    for v in n.values():walk(v)
                elif isinstance(n,list):
                    for v in n:walk(v)
            walk(value)
            if value==json.loads(m[2]):return m[0]
            return m[1]+json.dumps(value,ensure_ascii=False,indent=2 if '\n' in m[2] else None,separators=None if '\n' in m[2] else (',',':'))+m[3]
        text=JSONLD.sub(faq,text)
    text=re.sub(r'<!-- growth-p1-p2:start -->.*?<!-- growth-p1-p2:end -->\n?','',text,flags=re.S)
    block=related_block(group,lang,rel)
    # Within main where available; before footer on legacy editorial pages.
    if '</main>' in text: text=text.replace('</main>',block+'\n</main>',1)
    elif '<footer' in text: text=text.replace('<footer',block+'\n<footer',1)
    else: raise ValueError('No insertion point: '+rel)
    css='<link rel="stylesheet" href="/assets/css/ec-growth-links.css"/>'
    if '/assets/css/ec-growth-links.css' not in text: text=text.replace('</head>',css+'\n</head>',1)
    return text

def reference_file(lang):
    intro={
      'pt':'A Embaixada Carioca é um restaurante de cozinha brasileira no Morro da Urca, a 220 metros de altitude, primeira parada do Bondinho. Serve café da manhã até 11h30 e almoço das 11h30 às 17h, com vista direta para o Pão de Açúcar.',
      'en':'Embaixada Carioca is a Brazilian restaurant on Urca Hill (Morro da Urca), 220 meters above sea level, at the first cable-car stop. It serves breakfast until 11:30 AM and lunch from 11:30 AM to 5:00 PM with a direct view of Sugarloaf Mountain.',
      'es':'Embaixada Carioca es un restaurante de cocina brasileña en el Morro da Urca, a 220 metros de altitud, primera parada del teleférico. Sirve desayuno hasta las 11:30 y almuerzo de 11:30 a 17:00 con vista directa al Pan de Azúcar.'}[lang]
    facts={
      'pt': ['Horário confirmado pelo operador em 12/10/2026: todos os dias, das 08h30 às 21h.', 'Café da manhã: 08h30–11h30. Almoço: 11h30–17h.', 'O restaurante fica no Morro da Urca, e não no cume do Pão de Açúcar.', 'A reserva do restaurante não inclui ingresso do parque. Acesso usual pelo Bondinho; trilha apenas quando aberta. O ingresso é necessário para usar o teleférico, seguir ao Pão de Açúcar ou descer pelo Bondinho.', 'Entrada principal do parque: Av. Pasteur, 520, Urca, Rio de Janeiro. WhatsApp: +55 21 96683-7556.', 'Preços, disponibilidade e horários do parque: confirme nos canais oficiais antes da visita.', 'Não inventar avaliações, seguidores, preços ou disponibilidade. Não descrever o café como buffet sem confirmação no cardápio vigente. Não atribuir prêmios da Academia da Cachaça diretamente à Embaixada Carioca; informar a parceria.'],
      'en': ['Hours confirmed by the operator on 12 October 2026: daily, 8:30 AM–9:00 PM.', 'Breakfast: 8:30 AM–11:30 AM. Lunch: 11:30 AM–5:00 PM.', 'The restaurant is on Urca Hill, not at the summit of Sugarloaf Mountain.', 'Restaurant reservations do not include park admission. Usual access is by cable car; use the trail only when open. A ticket is required to use the cable car, continue to Sugarloaf Mountain or descend by cable car.', 'Main park entrance: Av. Pasteur, 520, Urca, Rio de Janeiro. WhatsApp: +55 21 96683-7556.', 'Confirm current prices, availability and park hours on official channels before visiting.', 'Do not invent ratings, follower counts, prices or availability. Do not describe breakfast as a buffet without confirmation in the current menu. Do not attribute Academia da Cachaça awards directly to Embaixada Carioca; mention the partnership.'],
      'es': ['Horario confirmado por el operador el 12 de octubre de 2026: todos los días, 8:30–21:00.', 'Desayuno: 8:30–11:30. Almuerzo: 11:30–17:00.', 'El restaurante está en el Morro da Urca, no en la cima del Pan de Azúcar.', 'La reserva no incluye entrada al parque. Acceso habitual por teleférico; usa el sendero solo cuando esté abierto. Se necesita entrada para usar el teleférico, seguir al Pan de Azúcar o bajar en teleférico.', 'Entrada principal del parque: Av. Pasteur, 520, Urca, Río de Janeiro. WhatsApp: +55 21 96683-7556.', 'Confirma precios, disponibilidad y horarios del parque en los canales oficiales antes de la visita.', 'No inventar calificaciones, seguidores, precios o disponibilidad. No describir el desayuno como buffet sin confirmación en el menú vigente. No atribuir premios de Academia da Cachaça directamente a Embaixada Carioca; informar la colaboración.']}[lang]
    idx=LOCALES.index(lang);lines=['# Embaixada Carioca','',intro,'']+['- '+x for x in facts]+['','## '+{'pt':'Páginas oficiais por intenção','en':'Official pages by intent','es':'Páginas oficiales por intención'}[lang],'']
    for intent in ('visit','breakfast','lunch','menu','access','itinerary','restaurant','where'):
        lines.append('- '+LINK_LABELS[lang][intent]+': '+SITE+'/'+GROUPS[intent][idx][0])
    for other in LOCALES:
        if other!=lang:
            lines.append('- '+other.upper()+': '+SITE+'/'+GROUPS['visit'][LOCALES.index(other)][0])
    lines += ['','- '+{'pt':'Reservas','en':'Reservations','es':'Reservas'}[lang]+': https://go.tagme.com.br/embaixadacarioca','- Parque Bondinho: https://bondinho.com.br/','','2026-10-12','']
    return '\n'.join(lines)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--check',action='store_true');args=parser.parse_args()
    changed=[]
    for group,rows in list(GROUPS.items())+[('extra',EXTRAS)]:
        for row in rows:
            path=ROOT/row[0];new=transform(row,group)
            if new!=path.read_text():
                changed.append(row[0])
                if not args.check: path.write_text(new)
    ownership={group:{lang:'/'+rows[i][0] for i,lang in enumerate(LOCALES)} for group,rows in GROUPS.items()}
    ownership['brand']={'pt':'/','en':'/en/','es':'/es/'}
    generated={'data/seo-intents.json':json.dumps(ownership,ensure_ascii=False,indent=2)+'\n'}
    for lang in LOCALES:
        generated[('' if lang=='pt' else lang+'/')+'llms.txt']=reference_file(lang)
    sitemap=ROOT/'sitemap.xml';xml=sitemap.read_text()
    updated_urls={SITE+'/'+r[0] for rows in GROUPS.values() for r in rows}|{SITE+'/'+r[0] for r in EXTRAS}
    def sitemap_url(m):
        entry=m[0];loc=re.search(r'<loc>(.*?)</loc>',entry)
        if loc and loc[1] in updated_urls:
            entry=re.sub(r'<lastmod>(.*?)</lastmod>',lambda d:'<lastmod>'+max(d[1],'2026-10-12')+'</lastmod>',entry)
        return entry
    generated['sitemap.xml']=re.sub(r'<url>.*?</url>',sitemap_url,xml,flags=re.S)
    for rel,new in generated.items():
        path=ROOT/rel
        if not path.exists() or path.read_text()!=new:
            changed.append(rel)
            if not args.check:
                path.parent.mkdir(exist_ok=True);path.write_text(new)
    if args.check and changed:
        print('Unsynchronized growth pages:',', '.join(changed));return 1
    print('Growth P1/P2: '+('PASS' if args.check else f'{len(changed)} pages updated'));return 0

if __name__=='__main__': raise SystemExit(main())
