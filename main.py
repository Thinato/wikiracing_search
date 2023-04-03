import pygame as pg
import pygame_gui as pg_gui
from requests import get
from math import inf
from lxml import etree
from node import Node
from urllib.parse import unquote
from numpy import random
from math import hypot, sin, cos, atan2
import json

pg.init()

w, h = 800,800
screen = pg.display.set_mode((w,h))
manager = pg_gui.UIManager((w, h))
clock = pg.time.Clock()

request_time = 800
request_last = inf

menu = pg_gui.elements.UIWindow(pg.Rect(400,0, 400, 400), window_display_title="Menu")

lbl_start = pg_gui.elements.UILabel(pg.Rect(10,10, 110, 32), container=menu, text="Pág. Inicial:")
txt_start = pg_gui.elements.UITextEntryLine(pg.Rect(120, 10, 240, 32), container=menu)
sel_start = pg_gui.elements.UISelectionList(pg.Rect(120, 40, 240, 100), container=menu, item_list=[], visible=0)
start_last_search = ""

lbl_final = pg_gui.elements.UILabel(pg.Rect(10,42, 110, 32), container=menu, text="Pág. Final:")
txt_final = pg_gui.elements.UITextEntryLine(pg.Rect(120, 42, 240, 32), container=menu)
sel_final = pg_gui.elements.UISelectionList(pg.Rect(120, 72, 240, 100), container=menu, item_list=[], visible=0)
final_last_search = ""

lbl_algorithm = pg_gui.elements.UILabel(pg.Rect(10, 74, 110, 32), container=menu, text="Algorítmo:")
cmb_algorithm = pg_gui.elements.UIDropDownMenu(relative_rect=pg.Rect(120, 74, 240, 32), container=menu, starting_option="Profundidade Limitada", options_list=["Profundidade Limitada", "Profundidade Iterativa", "A*"])


btn_create_nodes = pg_gui.elements.UIButton(pg.Rect(10,290, 150, 32), text="Criar Nós", container=menu)
# btn_create_nodes.disable()
btn_start_search = pg_gui.elements.UIButton(pg.Rect(170,290, 150, 32), text="Iniciar Busca", container=menu)
btn_start_search.disable()


nodes = []
visited_keys = set()
nodes_blit = dict()
with open('cache.json') as file:
    cache = json.load(file)

end_key = ''

def create_graph(key:str, depth_limit:int=4, index:int=0) -> bool:
    
    print('depth:', index,'- searching:', key)
    hps = []
    try:
        hps = cache[key]
    except:
        pass

    if hps:
        node = Node(key, initial_pos=(200,90*index+100))
        if node.key == end_key:
            with open('cache.json', 'w') as file:
                json.dump(cache, file)
            print('found', node.key)
            return node, index
        nodes.append(node)
    else:
        response = get(f"https://pt.wikipedia.org/wiki/{key}")
        if response.ok:

            node = Node(key, initial_pos=(200,90*index+100))
            if node.key == end_key:
                print('found', node.key)
                visited_keys.clear()
                nodes.clear()
                return node, index
            nodes.append(node)
            visited_keys.add(key)

            tree = etree.HTML(response.text)
            hps = [ unquote(hp.get("href")[6:]) for hp in list(tree.xpath('//div[@class="mw-parser-output"]/p/a[@href and (@class!="new" or not(@class))]'))]
            cache[key] = hps
        else:
            print(response)
            return False, 0
    
    if index == 0:
        nodes_blit[0] = [node]
        
    for hp in hps:
        next_index = index+1
        if next_index >= depth_limit:
            continue
        node_hp = create_graph(hp, depth_limit, index=next_index)
        if node_hp and node_hp[0]:
            node_hp[0].parent = node
            if next_index not in nodes_blit.keys():
                nodes_blit[next_index] = []
            nodes_blit[next_index].append(node_hp[0])
            return node, index
        else:
            continue
        
    


def dist(node1:object, node2:object) -> float:
    return hypot(node1.pos.x - node2.pos.x, node1.pos.y - node2.pos.y)

def get_angle(node1:object, node2:object) -> float:
    return atan2(node1.pos.y - node2.pos.y, node1.pos.x - node2.pos.x)

def calc_collision(node1:object, dt:float) -> None:
    for node2 in nodes:
        if node1 != node2:
            dx, dy = 0,0
            if dist(node1, node2) < 50:
                angle = get_angle(node1, node2)
                dx, dy = cos(angle), sin(angle)
            node1.move((dx, dy), dt, (0,0,800,800))

while True:
    dt = clock.tick() / 1000
    pg.display.set_caption(str(round(clock.get_fps(),3)))
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            exit()
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                if menu.visible:
                    menu.hide()
                else:
                    menu.show()
                    sel_start.hide()
                    sel_final.hide()
        elif event.type == pg_gui.UI_TEXT_ENTRY_FINISHED:
            if event.ui_element == txt_start:
                sel_start.set_item_list([])
                response = get(f"https://pt.wikipedia.org/w/rest.php/v1/search/title?q={txt_start.get_text()}&limit=10")
                res_start = response.json()
                sel_start.add_items([ result['key'] for result in res_start['pages'] ])
                sel_start.show()
                txt_final.hide()
                cmb_algorithm.hide()
                start_last_search = txt_start.get_text()
                nodes = []
            elif event.ui_element == txt_final:
                sel_final.set_item_list([])
                response = get(f"https://pt.wikipedia.org/w/rest.php/v1/search/title?q={txt_final.get_text()}&limit=10")
                res_final = response.json()
                sel_final.add_items([ result['key'] for result in res_final['pages'] ])
                sel_final.show()
                cmb_algorithm.hide()
                end_key = txt_final.get_text()
                nodes = []
        elif event.type == pg_gui.UI_SELECTION_LIST_DOUBLE_CLICKED_SELECTION:
            if event.ui_element == sel_start:
                txt_start.set_text( event.text )
                sel_start.hide()
                txt_final.show()
                cmb_algorithm.show()
            elif event.ui_element == sel_final:
                txt_final.set_text( event.text )
                sel_final.hide()
                cmb_algorithm.show()
        
        elif event.type == pg_gui.UI_BUTTON_PRESSED:
            if event.ui_element == btn_create_nodes:
                end_key = txt_final.get_text()
                create_graph(txt_start.get_text())

        manager.process_events(event)

    screen.fill((0,0,0))

    # for node in nodes_blit:
    #     calc_collision(node)
    #     node.update(screen)

    
    for key in list(nodes_blit.keys()):
        for node in nodes_blit[key]:
            if node.parent:
                pg.draw.line(screen, (0,255,0), node.pos, node.parent.pos)

    for key in list(nodes_blit.keys()):
        for node in nodes_blit[key]:
            # calc_collision(node, dt)
            node.update(screen)


    manager.update(dt)
    manager.draw_ui(screen)
    pg.display.flip()