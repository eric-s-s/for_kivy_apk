# pylint: disable=no-member, unused-argument, no-name-in-module
'''requires kivy and kivy garden graph'''
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.dropdown import DropDown
from kivy.properties import (NumericProperty, ListProperty, StringProperty,
                             BooleanProperty, ObjectProperty)
from kivy.clock import Clock
from kivy.uix.carousel import Carousel
from kivy.graphics.vertex_instructions import Line
import dicestats as ds
import tableinfo as ti
from longintmath import long_int_div as li_div
from itertools import cycle as itertools_cycle
from kivy.garden.graph import MeshLinePlot


#tools
FLASH_DELAY = 0.5

def main():
    '''gets the current diceplatform so all can call it'''
    return App.get_running_app().root



# kv file line NONE
class FlashButton(Button):
    '''a button that flashes for FLASH_DELAY time after pressed, so you know you
    done taht press real clear-like. don't forget to assign on_press using
    self.delay or you won't see the flash.'''
    def __init__(self, **kwargs):
        super(FlashButton, self).__init__(**kwargs)
    @staticmethod
    def delay(function, *args):
        '''delays a function call so that button has time to flash.  use with
        on_press=self.delay(function, function_args)'''
        Clock.schedule_once(lambda delta_time: function(*args), FLASH_DELAY)
    def on_press(self, *args):
        '''sets background to flash on press'''
        self.color = [1, 0, 0, 1]
        self.background_color = [0.2, 0.2, 1, 1]
        Clock.schedule_once(self.callback, FLASH_DELAY)
    def callback(self, delta_time):
        '''sets background to normal'''
        self.color = [1, 1, 1, 1]
        self.background_color = [1, 1, 1, 1]
# kv file line NONE
class FlashLabel(Button):
    '''a label that flashes for FLASH_DELAY when text is added by add_text.
    can be turned off with boolean do_flash'''
    def __init__(self, **kwargs):
        super(FlashLabel, self).__init__(**kwargs)
        self.background_normal = ''
    def add_text(self, text, do_flash=True):
        '''flahes (or not) when text is changed'''
        self.text = text
        self.color = [1, 1, 1, 1]
        self.background_color = [0, 0, 0, 0]
        if do_flash:
            self.color = [1, 0, 0, 1]
            self.background_color = [0.2, 0.2, 1, 0.2]
            Clock.schedule_once(self.callback, FLASH_DELAY)
    def callback(self, delta_time):
        '''reset background and color after delay'''
        self.color = [1, 1, 1, 1]
        self.background_color = [0, 0, 0, 0]
# kv file line NONE
class PlusMinusButton(FlashButton):
    '''init - numer=int.  self.number is stored and text is +/- the number
    don't forget to assign on_press using self.delay to see the flash.'''
    def __init__(self, number, **kwargs):
        super(PlusMinusButton, self).__init__(**kwargs)
        self.number = number
        self.text = '{:+}'.format(self.number)
# kv file line 6
class SizeButton(FlashButton):
    '''a button for sizing a die.  label is "D(diesize)" defaults to 1.
    don't forget to assign on_press using self.delay to see the flash.'''
    die_size = NumericProperty(1)

# kv file line NONE
class NumberInput(Button):
    '''a button that opens a number pad for input. fire input events using
    on_number_val'''
    number_val = StringProperty('0')
    def __init__(self, **kwargs):
        super(NumberInput, self).__init__(**kwargs)
        pad = StackLayout(orientation='lr-tb')
        texts = itertools_cycle(['+', '-', '='])
        for digit in range(1, 10):
            pad.add_widget(Button(text=str(digit), size_hint=(0.29, 0.25),
                                  on_press=self.add_digit))
            if digit % 3 == 0:
                pad.add_widget(Button(text=next(texts), size_hint=(0.1, 0.25),
                                      on_press=self.plus_minus))
        pad.add_widget(Button(text='BS', size_hint=(0.29, 0.25),
                              on_press=self.back_space))
        pad.add_widget(Button(text='0', size_hint=(0.29, 0.25),
                              on_press=self.add_digit))
        pad.add_widget(Button(text='ENT', size_hint=(0.39, 0.25),
                              on_press=self.enter_val))
        self.num_pad = Popup(title='', content=pad, size_hint=(0.8, 0.5),
                             pos_hint={'x':0.1, 'y':0})
        self.text = ''
        self.background_color = (0.4, 0.2, 1.0, 0.8)
        self.bind(on_release=self.open_pad)
        self.to_add = 0
        self.sign = 1
    def add_digit(self, btn):
        '''fired when 0-9 is pressed'''
        if self.num_pad.title == ' ':
            self.num_pad.title = btn.text
        else:
            self.num_pad.title += btn.text
    def back_space(self, btn):
        '''fired when BS is pressed'''
        if self.num_pad.title != ' ':
            if self.num_pad.title[:-1]:
                self.num_pad.title = self.num_pad.title[:-1]
            else:
                self.num_pad.title = ' '
    def open_pad(self, btn):
        '''no new info'''
        self.to_add = 0
        self.sign = 1
        self.num_pad.open(self)
        self.num_pad.title = ' '
        self.num_pad.title_size = self.num_pad.height/8
    def plus_minus(self, btn):
        '''uses self.to_add and self.sign to do plus, minus, equals.  on equals,
        makes title to self.to_add and resets'''
        if self.num_pad.title != ' ':
            self.to_add += int(self.num_pad.title) * self.sign
        if btn.text == '-':
            self.sign = -1
        if btn.text == '+':
            self.sign = 1
        if btn.text == '=':
            self.num_pad.title = str(self.to_add)
            self.to_add = 0
            self.sign = 1
        else:
            self.num_pad.title = ' '
    def enter_val(self, btn):
        '''when you press enter, changes the number_val to fire event. so if you
        close the window without enter, you don't change any values'''
        self.num_pad.dismiss()
        if self.num_pad.title != ' ':
            self.text = self.num_pad.title
            #so that on_number_val will fire on enter even if number didn't change
            self.number_val = self.num_pad.title + ' '
            self.number_val = self.num_pad.title

#for weightpopup
# kv file line NONE
class NumberSelect(Button):
    '''a button that pops up number selection based on it's stop/start. the text
    is a combination of a title and the number selected.  the place_hold is for
    use with assigning a roll number and being able to retrieve it easily'''
    number_value = NumericProperty(0)
    place_hold = NumericProperty(0)
    title = StringProperty('')
    def __init__(self, start, stop, **kwargs):
        super(NumberSelect, self).__init__(**kwargs)
        self.the_range = range(start, stop+1)

        self.background_color = (0.6, 0.4, 1.0, 1.0)
        self.bind(on_release=self.open_pad)
        self.bind(title=self._set_text)
        self.bind(number_value=self._set_text)
        self.halign = 'center'
    def open_pad(self, *args):
        '''creates a popup pad and opens it'''
        pad = SelectPad(self, size_hint=(0.8, 0.5), pos_hint={'x':0.1, 'y':0})
        pad.open()

    def _set_text(self, instance, text):
        '''the private method that listens for changes in title or chosen number
        and updates button text'''
        self.text = self.title + '\n%s' % self.number_value

# kv file line NONE
class SelectPad(Popup):
    '''a popup that is called by NumberSelect.  creates a number pad of number
    choices.'''
    def __init__(self, parent_btn, **kwargs):
        super(SelectPad, self).__init__(**kwargs)
        self.parent_btn = parent_btn

        self.content = StackLayout(orientation='lr-tb', size_hint=(1, 1))
        y_hint_ = 0.01* int(100 /(1 + len(self.parent_btn.the_range)//3))
        for number in self.parent_btn.the_range:
            self.content.add_widget(Button(text=str(number),
                                           size_hint=(0.33, y_hint_),
                                           on_press=self.record_number))
        self.title = self.parent_btn.title
        self.title_align = 'center'
    def record_number(self, btn):
        '''assigns button's number to parent'''
        self.parent_btn.number_value = int(btn.text)
        self.dismiss()
# kv file line 9
class WeightsPopup(Popup):
    '''the popup called when weighting a die'''
    def __init__(self, parent_obj, **kwargs):
        super(WeightsPopup, self).__init__(**kwargs)
        self.parent_obj = parent_obj
        self.pack()
    def pack(self):
        '''sizes popup appropiately and packs with right number of weights'''
        spacing = 10.
        cols_within_frame = 3
        die_size = self.parent_obj.die_size
        col_width = int(self.parent_obj.width / cols_within_frame)
        add_drag = False
        cols = ((die_size)//10 +1)
        if cols > cols_within_frame:
            cols = ((die_size+2)//10 +1)
            add_drag = True
            drag_it = Label(text='DRAG\n====>', bold=True)
        height = int(self.parent_obj.height* 0.9)
        sz_hint = ((col_width - spacing)/(cols*col_width), 0.1 * (height-spacing)/height)

        self.size = (min(1.1 * cols*col_width, self.parent_obj.width),
                     self.parent_obj.height)
        contents = self.ids['contents']
        contents.clear_widgets()
        contents.size = (cols*col_width*0.88, height)
        contents.spacing = spacing
        if add_drag:
            drag_it.size_hint = sz_hint
            contents.add_widget(drag_it)
            contents.add_widget(Button(on_press=self.record_weights,
                                       text='record\nweights', size_hint=sz_hint))

        for roll in range(1, die_size + 1):
            weighter = NumberSelect(0, 10, number_value=1, size_hint=sz_hint,
                                    place_hold=roll)
            weighter.title = 'weight for %s' % (roll)
            contents.add_widget(weighter)
        contents.add_widget(Button(on_press=self.record_weights,
                                   text='record\nweights', size_hint=sz_hint))

    def record_weights(self, button):
        '''records the weights from the weight popup'''
        new_weights = {}
        for child in self.ids['contents'].children[:]:
            if isinstance(child, NumberSelect):
                new_weights[child.place_hold] = child.number_value
        if sum(new_weights.values()) == 0:
            new_weights = {}
        self.parent_obj.dictionary = dict(new_weights.items())
        self.parent_obj.assign_die()
        self.dismiss()

# kv file line NONE
class PlotObject(Label):
    '''a label taht contains all the needed info for kivy.garden.graph'''
    pts = ListProperty([(0, 1)])
    orig = ListProperty([(0,1)])
    dice = ListProperty([])
    x_min = NumericProperty(0)
    x_max = NumericProperty(0)
    y_min = NumericProperty(0)
    y_max = NumericProperty(1)

    def __eq__(self, other):
        return self.pts == other.pts and self.text == other.text
    def __ne__(self, other):
        return not self == other
# kv file line NONE
class ObjectButton(Button):
    '''simply a button with an object attached'''
    obj = ObjectProperty(PlotObject())
# kv file line 22
class PlotPopup(Popup):
    '''popup containing the graph'''
    def __init__(self, **kwargs):
        super(PlotPopup, self).__init__(**kwargs)
        self._plot_list = []
        self.legend = DropDown(dismiss_on_select=False)
    def add_list(self, new_list):
        '''main funciton to make a graph'''
        self._plot_list = new_list[:]
        self.make_graph()
        self.make_legend()
    def make_graph(self):
        '''makes a graph and plots'''
        colors = itertools_cycle([
            [0.2, 1.0, 0, 1], [1, 0, 0.2, 1], [0.8, 1.0, 0.1, 1],
            [0.6, 0, 0.8, 1], [1, 0.4, 0.2, 1], [1, 0.8, 0, 1],
            [0, 0.2, 1, 1]
            ])
        x_range = []
        y_range = []
        y_ticks = [0.05, 0.1, 0.2, 0.5, 1, 5, 10]
        x_ticks = [1, 2, 5, 10, 20, 30, 50, 100, 200, 300, 500, 1000, 2000, 5000]
        for plot_obj in self._plot_list:
            plot_obj.color = next(colors)
            self.ids['graph'].add_plot(MeshLinePlot(points=plot_obj.pts,
                                                    color=plot_obj.color))
            if x_range:
                x_range[0] = min(x_range[0], plot_obj.x_min)
                x_range[1] = max(x_range[1], plot_obj.x_max)
            else:
                x_range = [plot_obj.x_min, plot_obj.x_max]
            if y_range:
                y_range[1] = max(y_range[1], plot_obj.y_max)
            else:
                y_range = [0, plot_obj.y_max]
        x_tick_num = (x_range[1]-x_range[0])/9.
        for tick in x_ticks:
            if x_tick_num < tick:
                x_tick_num = tick
                break
        y_tick_num = (y_range[1]-y_range[0])/20.
        for tick in y_ticks:
            if y_tick_num < tick:
                y_tick_num = tick
                break
        x_range[0] -= x_range[0] % x_tick_num
        current = self.ids['graph'].font_size
        factor = 1
        if x_tick_num > 49:
            factor = 0.75
        if x_tick_num > 99:
            factor = 0.66
        if x_tick_num > 499:
            factor = 0.5

        self.ids['graph'].font_size = int(factor * current)
        self.ids['graph'].x_ticks_major = x_tick_num
        self.ids['graph'].y_ticks_major = y_tick_num
        self.ids['graph'].xmin = x_range[0]
        self.ids['graph'].ymin = -y_tick_num
        self.ids['graph'].xmax = x_range[1]
        self.ids['graph'].ymax = y_range[1]

    def make_legend(self):
        '''created the dropdown menu that's called by 'legend' button'''
        for plot_obj in self._plot_list:

            btn = ObjectButton(text=plot_obj.text, size_hint=(None, None),
                               height=80, obj=plot_obj, color=plot_obj.color,
                               valign='middle')
            btn.bind(on_release=lambda btn: self.legend.select(btn.obj))
            self.legend.add_widget(btn)
        self.legend.on_select = self.flash_plot
        self.ids['legend'].bind(on_release=self.legend.open)
        self.ids['legend'].bind(on_release=self.resize)
        self.legend.bind(on_dismiss=self.shrink_button)
    def shrink_button(self, event):
        '''make legend button small again after dismiss drop down'''
        self.ids['legend'].width = self.ids['legend'].texture_size[0]
    def resize(self, *args):
        '''on release, resize drop down to fit widest button'''
        widths = [self.ids['legend'].texture_size[0]]
        for btn in self.legend.children[0].children:
            raw_lines = (btn.texture_size[0] + 10.)/main().width
            single_line_ht = btn.texture_size[1]
            lines = int(raw_lines)
            if lines < raw_lines:
                lines += 1
            split_at = len(btn.text)/lines
            if len(btn.text) % lines:
                split_at += 1
            #make long btn.text multiline
            new_text_lst = []
            copy = btn.text
            while len(copy) > split_at:
                new_text_lst.append(copy[:split_at])
                copy = copy[split_at:]
            new_text_lst.append(copy)
            btn.text = '\n'.join(new_text_lst)

            btn.width = min(btn.texture_size[0] + 10, main().width)
            btn.height = max(self.ids['legend'].height, single_line_ht * lines)
            widths.append(btn.width)
        self.ids['legend'].width = max(widths)
    def flash_plot(self, obj, second_time=False):
        '''on press, highlight selected graph'''
        for plot in self.ids['graph'].plots:
            if plot.points == obj.pts:
                temp_color = plot.color
                for index in range(3):
                    temp_color[index] = 1-temp_color[index]
                temp_color = [1, 1, 1, 1]
                self.ids['graph'].remove_plot(plot)
                new_plot = MeshLinePlot(points=obj.pts, color=temp_color)
                self.ids['graph'].add_plot(new_plot)
        if second_time:
            Clock.schedule_once(lambda dt: self._callback(obj, True), FLASH_DELAY)
        else:
            Clock.schedule_once(lambda dt: self._callback(obj), FLASH_DELAY)
    def _callback(self, obj, second_time=False):
        '''resets graph to original color'''
        for plot in self.ids['graph'].plots:
            if plot.points == obj.pts:
                plot.color = obj.color

        if not second_time:
            Clock.schedule_once(lambda dt: self.flash_plot(obj, True), FLASH_DELAY)

# kv file line 51
class PlotCheckBox(BoxLayout):
    '''a checkbox with associated label and function to return label if box checked'''
    obj = ObjectProperty(PlotObject())
    text = StringProperty('')
    active = BooleanProperty(False)
    def __init__(self, reloader=True, **kwargs):
        super(PlotCheckBox, self).__init__(**kwargs)
        self.ids['check_box'].bind(active=self._change_active)
        self.text = self.obj.text
        if reloader:
            self.ids['scroller'].size_hint = (0.7, 1)
            btn = Button(text='reload', size_hint=(0.2, 0.6), valign='middle',
                         halign='center', max_lines=1, 
                         on_press=self.reload_obj)
            btn.texture_size=btn.size
            self.add_widget(btn)
    def reload_obj(self, btn):
        main().request_reload(self.obj)
        

    def _change_active(self, checkbox, value):
        '''a helper function to bind checkbox active to main active'''
        self.active = self.ids['check_box'].active
    def two_line_text(self, split_char):
        '''makes a new two-line display label while preserving original in'''
        self.text = self.obj.text
        if self.ids['scroller'].width < len(self.text)*self.ids['label'].font_size/4:
            line_1 = self.text[:len(self.text)/2]
            line_2 = self.text[len(self.text)/2:]
            self.text = line_1 + line_2.replace(split_char, '\n', 1)


# kv file line 68
class PageBox(BoxLayout):
    '''a box that splits a long text into pages. displays labels of requested page.
    default size ratio is TITLE = 0.15, buttons = 0.05, text=0.8.'''
    def __init__(self, **kwargs):
        super(PageBox, self).__init__(**kwargs)
        self.pages = ['']
        self.current_page = 0
    def reset_sizes(self, ratios):
        '''reset font_size = f_size,
        [title ratio, button ratio, text ratio] = ratios'''
        self.ids['page_box_title'].size_hint_y = ratios[0]
        self.ids['buttons_container'].size_hint_y = ratios[1]
        self.ids['text_container'].size_hint_y = ratios[2]
    def set_title(self, title):
        '''title is a string'''
        self.ids['page_box_title'].text = title

    def text_check(self, text):
        '''passes text input to show_page'''
        if text:
            self.show_page(int(text) - 1)
    def show_page(self, number):
        '''display page number (number % total pages)'''
        number = number % len(self.pages)
        self.current_page = number
        self.ids['text_container'].text = self.pages[number]
        self.ids['text_container'].text_size = self.ids['text_container'].size
        self.ids['jump_to'].text = str(number + 1)
    def set_text(self, new_text, fudge_factor=0.83):
        '''this sets the page box with a new text which it splits into pages
        according to lines_per_page = fudge_factor * box_height/font_size.
        fudge_factor=0.83 works here for spaces bewteen lines of text, but it's
        set-able just in case.'''
        lines_per_page = int(self.ids['text_container'].height * fudge_factor/
                             float(self.ids['text_container'].font_size))
        def page_maker(text, line_limit):
            '''helper function.  splits a str into lst of strings according to
            line_limit.  adds enout \n to final string so all strings have same
            # of lines.'''
            text = text.rstrip('\n')
            lines = text.split('\n')
            num_lines = len(lines)
            out = []
            if num_lines % line_limit == 0:
                pages = num_lines // line_limit
            else:
                pages = num_lines // line_limit + 1
            for count in range(0, (pages - 1)*line_limit, line_limit):
                page = '\n'.join(lines[count:count+line_limit])
                out.append(page)
            last_page = lines[(pages - 1)*line_limit:]
            extra_lines = (line_limit - len(last_page)) * [' ']
            last_page = '\n'.join(last_page + extra_lines)
            out.append(last_page)
            return out[:]
        self.pages = page_maker(new_text, lines_per_page)
        self.ids['page_total'].text = '/%s' % (len(self.pages))
        self.show_page(self.current_page)
# kv file line 131
class AddRmDice(BoxLayout):
    '''a box taht calls add(num, die) and remove(num, die) funtion
    when pressed.
    '''
    def __init__(self, die, **kwargs):
        super(AddRmDice, self).__init__(**kwargs)
        self._die = die
        self.small = 20
        self.medium = 100
    def assign_die(self, die):
        '''can re-assign number and die after creation.'''
        self._die = die
    def addrm(self, btn):
        '''what is called by the on_press method for packed buttons. the buttons
        are FlashButtons, so they must call btn.delay()'''
        times = btn.number
        main_obj = main()
        if times < 0:
            btn.delay(main_obj.request_remove, abs(times), self._die)
        else:
            btn.delay(main_obj.request_add, times, self._die)
    def assign_buttons(self, label_number, only_add=False, do_flash=True):
        '''assigns buttons to the box.  label_number is an int.  0 displays the
        str(die), otherwise die.multiply_str(number). only_add controls if there
        are minus buttons.  do_flash flashes the label'''
        self.clear_widgets()
        if self._die.get_size() < self.small:
            buttons = 3
        elif self.small <= self._die.get_size() < self.medium:
            buttons = 2
        else:
            buttons = 1
        sz_hnt_x = round(1./(2*buttons + 2), 2)
        if not only_add:
            for number in range(buttons - 1, -1, -1):
                btn = PlusMinusButton(-10**number, size_hint=(sz_hnt_x, 1))
                btn.bind(on_press=self.addrm)
                self.add_widget(btn)
        if label_number == 0:
            die_string = str(self._die)
        else:
            die_string = self._die.multiply_str(label_number)
        flash = FlashLabel()
        flash.size_hint = (sz_hnt_x * 2, 1)
        self.add_widget(flash)
        flash.add_text(die_string, do_flash=do_flash)
        for number in range(buttons):
            btn = PlusMinusButton(10**number, size_hint=(sz_hnt_x, 1))
            btn.bind(on_press=self.addrm)
            self.add_widget(btn)

#big_boxes
# kv file line 137
class ChangeBox(GridLayout):
    '''displays current dice and allows to change. parent app is what's called
    for dice actions and info updates. all calls are
    self.parent_app.request_something(*args).'''
    def __init__(self, **kwargs):
        super(ChangeBox, self).__init__(**kwargs)
        self.cols = 1
        self.old_dice_list = []
    def update(self):
        '''updates the current dice after add, rm or clear'''
        dice_list = main().request_info('dice_list')
        self.clear_widgets()
        max_height = self.height/10
        reset = Button(on_press=main().request_reset, text='reset table',
                       size_hint=(1, None), height=0.75*max_height)
        self.add_widget(reset)
        if dice_list:
            new_height = min((self.height - reset.height) / len(dice_list),
                             max_height)
        for die, number in dice_list:
            if (die, number) in self.old_dice_list:
                changed = False
            else:
                changed = True
            add_rm = AddRmDice(die, size_hint=(0.8, None), height=new_height)
            add_rm.assign_buttons(number, do_flash=changed)
            self.add_widget(add_rm)
        self.old_dice_list = dice_list

# kv file line 145
class AddBox(BoxLayout):
    '''box for adding new dice.  parent app is what's called for dice actions and
    info updates. all calls are self.parent_app.request_something(*args).'''
    def __init__(self, **kwargs):
        super(AddBox, self).__init__(**kwargs)
        self.mod = 0
        self.dictionary = {}
        self.die_size = 6
        self.add_it = AddRmDice(ds.Die(6), size_hint=(1, 1))
        self.add_it.assign_buttons(0, only_add=True, do_flash=True)
    def initialize(self):
        '''how the box is packed'''
        self.ids['add_it'].add_widget(self.add_it)
        for number in [2, 4, 6, 8, 10, 12, 20, 100]:
            btn = SizeButton(die_size=number)
            btn.bind(on_press=self.assign_size_btn)
            self.ids['presets'].add_widget(btn)
    def update(self):
        '''called by main app at dice change'''
        self.ids['current'].text = (main().request_info('table_str').
                                    replace('\n', ' \\ '))
    def assign_size_btn(self, btn):
        '''assigns the die size and die when a preset btn is pushed'''
        self.dictionary = {}
        self.die_size = btn.die_size
        self.assign_die()
    def assign_size_text(self, text):
        '''asigns the die size and die when text is entered'''
        self.dictionary = {}
        top = 200
        bottom = 2
        int_string = text
        if int_string:
            self.die_size = int(text)
            if self.die_size < bottom:
                self.die_size = bottom
            if self.die_size > top:
                self.die_size = top
        if text != str(self.die_size):
            self.ids['custom_input'].text = str(self.die_size)
        self.assign_die()
    def assign_mod(self):
        '''assigns a die modifier and new die when slider is moved'''
        self.mod = int(self.ids['modifier'].value)
        self.assign_die()
    def assign_die(self):
        '''all changes to size, mod and weight call this function'''
        if self.dictionary:
            if self.mod == 0:
                die = ds.WeightedDie(self.dictionary)
            else:
                die = ds.ModWeightedDie(self.dictionary, self.mod)
        else:
            if self.mod == 0:
                die = ds.Die(self.die_size)
            else:
                die = ds.ModDie(self.die_size, self.mod)
        self.add_it.assign_die(die)
        self.add_it.assign_buttons(0, only_add=True, do_flash=True)
    def add_weights(self):
        '''opens the weightpopup and sizes accordingly'''
        popup = WeightsPopup(self)
        popup.open()



# kv file line 222
class InfoBox(BoxLayout):
    '''displays basic info about the die. parent app is what's called for dice
    actions and info updates. all calls are
    self.parent_app.request_something(*args).'''
    def __init__(self, **kwargs):
        super(InfoBox, self).__init__(**kwargs)
    def initialize(self):
        '''called at main app init. workaround for .kv file loading before .py'''
        self.ids['weight_info'].reset_sizes([0.08, 0.1, 0.82])
        self.ids['weight_info'].set_title('full weight info')
    def update(self):
        '''updates all the info in box.'''
        values_min, values_max = main().request_info('range')
        mean = main().request_info('mean')
        stddev = main().request_info('stddev')
        stat_text = ('the range of numbers is %s-%s\nthe mean is %s\nthe stddev is %s'
                     % (values_min, values_max, round(mean, 4), stddev))
        self.ids['stat_str'].text = stat_text
        self.ids['dice_table_str'].text = '\n' + main().request_info('table_str')
        to_set = main().request_info('weights_info').replace('a roll of', '')
        to_set = to_set.replace(' a ', ' ')
        to_set = to_set.replace(' of ', ': ')
        self.ids['weight_info'].set_text(to_set)
# kv file line 244
class GraphBox(BoxLayout):
    '''buttons for making graphs.  parent app is what's called for dice actions
    and info updates. all calls are self.parent_app.request_something(*args).'''
    def __init__(self, **kwargs):
        super(GraphBox, self).__init__(**kwargs)
        self.plot_history = []
        self.plot_current = PlotObject(text='')
    def initialize(self):
        '''called at main app init. workaround for .kv file loading before .py'''
        self.ids['graph_space'].add_widget(PlotCheckBox(size_hint=(1, 0.5)))
    def update(self):
        '''updates the current window to display new graph history and current
        table to graph'''
        new_string = main().request_info('table_str').replace('\n', ' \\ ')
        self.plot_current = PlotObject(text=new_string)
        self.ids['graph_space'].clear_widgets()
        self.ids['graph_space'].add_widget(Label(text='past graphs',
                                                 size_hint=(1, 0.1)))
        for item in self.plot_history[::-1]:
            check = PlotCheckBox(obj=item, size_hint=(1, 0.1), active=False)
            check.two_line_text('\\')
            
            self.ids['graph_space'].add_widget(check)
        self.ids['graph_space'].add_widget(Label(text='new table',
                                                 size_hint=(1, 0.1)))
        check = PlotCheckBox(size_hint=(1, 0.1), active=True, 
                             obj=self.plot_current, reloader=False)
        check.two_line_text('\\')
        self.ids['graph_space'].add_widget(check)
    def graph_it(self):
        '''prepares plot and calls PlotPopup'''
        to_plot = []
        for item in self.ids['graph_space'].children[1:]:
            if isinstance(item, PlotCheckBox):
                if item.active:
                    to_plot.append(item.obj)
        if self.ids['graph_space'].children[0].active and self.plot_current.text:
            self.plot_current = main().request_plot_object()
            if self.plot_current not in self.plot_history:
                self.plot_history.insert(0, self.plot_current)
            if self.plot_current not in to_plot:
                to_plot.insert(0, self.plot_current)
        self.update()
        if to_plot:
            plotter = PlotPopup()
            plotter.add_list(to_plot)
            plotter.open()
    def clear_all(self):
        '''clear graph history'''
        self.plot_history = []
        self.update()
    def clear_selected(self):
        '''clear selected checked items from graph history'''
        new_history = []
        for index in range(len(self.plot_history)):
            if not self.ids['graph_space'].children[index + 2].active:
                new_history.append(self.plot_history[index])
        self.plot_history = new_history[:]
        self.update()
# kv file line 279
class StatBox(BoxLayout):
    '''box for getting and displaying stats about rolls. parent app is what's
    called for dice actions and info updates. all calls are
    self.parent_app.request_something(*args).'''
    def __init__(self, **kwargs):
        super(StatBox, self).__init__(**kwargs)
        self.text_lines = 1

    def update(self):
        '''called when dice list changes.'''
        val_min, val_max = main().request_info('range')
        self.ids['stop_slider'].min = val_min
        self.ids['start_slider'].min = val_min
        self.ids['stop_slider'].max = val_max
        self.ids['start_slider'].max = val_max
        mean = main().request_info('mean')
        stddev = main().request_info('stddev')
        self.ids['table_info'].text = (('the range of numbers is %s-%s\nthe ' +
                                        'mean is %s\nthe stddev is %s') %
                                       (val_min, val_max, round(mean, 4), stddev))
        self.show_stats()
    def assign_text_value(self, box='start'):
        '''called by text_input to assign that value to sliders and show stats'''
        val_min, val_max = main().request_info('range')
        change_str = self.ids[box + '_slider_text'].text
        if change_str:
            if int(change_str) < val_min:
                val_new = val_min
            elif int(change_str) > val_max:
                val_new = val_max
            else:
                val_new = int(change_str)
            self.ids[box+'_slider'].value = val_new

        self.show_stats()

    def show_stats(self):
        '''the main function. displays stats of current slider values.'''
        val_1 = int(self.ids['stop_slider'].value)
        val_2 = int(self.ids['start_slider'].value)
        self.ids['stop_slider_text'].text = str(val_1)
        self.ids['start_slider_text'].text = str(val_2)
        stat_list = range(min(val_1, val_2), max(val_1, val_2) + 1)
        stat_info =  main().request_stats(stat_list)
        stat_text = ('\n    {stat[0]} occurred {stat[1]} times\n'+
                     '    out of {stat[2]} total combinations\n\n'+
                     '    that\'s a one in {stat[3]} chance\n'+
                     '    or {stat[4]} percent')
        self.ids['stat_text'].text = stat_text.format(stat=stat_info)
# kv file line NONE
class AllRollsBox(PageBox):
    '''a pagebox that display the frequency for each roll in the table. parent
    app is what's called for dice actions and info updates. all calls are
    self.parent_app.request_something(*args).'''
    def __init__(self, **kwargs):
        super(AllRollsBox, self).__init__(**kwargs)
    def initialize(self):
        '''called by main app after init'''
        self.set_title('here are all the rolls and their frequency')
        self.ids['page_box_title'].font_size *= 0.75
    def update(self):
        '''rewrites after dice change'''
        text = main().request_info('all_rolls')
        self.set_text(text)

# kv file line 353
class DicePlatform(Carousel):
    '''the main box.  the parent_app.'''
    def __init__(self, **kwargs):
        super(DicePlatform, self).__init__(**kwargs)
        self._table = ds.DiceTable()
        self.direction = 'right'
        self.loop = 'true'
        self.initializer()
    def initializer(self):
        '''initializes various values that couldn't be written before both .py
        file and .kv file were called'''
        self.ids['add_box'].initialize()
        self.ids['graph_box'].initialize()
        self.ids['info_box'].initialize()
        self.ids['all_rolls_box'].initialize()
    def updater(self):
        '''updates appropriate things for any die add or remove'''
        self.ids['change_box'].update()
        self.ids['stat_box'].update()
        self.ids['graph_box'].update()
        self.ids['all_rolls_box'].update()
        self.ids['info_box'].update()
        self.ids['add_box'].update()

    def request_info(self, request):
        '''returns requested info to child widget'''
        requests = {'range': [self._table.values_range, ()],
                    'mean': [self._table.mean, ()],
                    'stddev': [self._table.stddev, ()],
                    'table_str': [str, (self._table,)],
                    'weights_info': [self._table.weights_info, ()],
                    'dice_list': [self._table.get_list, ()],
                    'all_rolls': [ti.full_table_string, (self._table,)]}
        command, args = requests[request]
        return command(*args)
    def request_stats(self, stat_list):
        '''returns stat info from a list'''
        return ti.stats(self._table, stat_list)
    def request_plot_object(self):
        '''converts the table into a PlotObject'''
        new_object = PlotObject(text=str(self._table).replace('\n', ' \\ '))
        graph_pts = ti.graph_pts(self._table, axes=False)
        y_vals = [pts[1] for pts in graph_pts]

        new_object.x_min, new_object.x_max = self._table.values_range()
        new_object.y_min = min(y_vals)
        new_object.y_max = max(y_vals)
        new_object.pts = graph_pts
        new_object.orig = self._table.frequency_all()
        new_object.dice = self._table.get_list()
        return new_object
    
    def request_reload(self, plot_obj):
        self._table = ds.DiceTable()
        for die, number in plot_obj.dice:
            self._table.update_list(number, die)
        self._table.add(1, plot_obj.orig)
        self.updater()
        
    def request_add(self, number, die):
        '''adds dice to table'''
        self._table.add_die(number, die)
        self.updater()
    def request_remove(self, number, die):
        '''safely removes dice from table. if too many removed, removes all of
        that kind of dice'''
        current = self._table.number_of_dice(die)
        if number > current:
            self._table.remove_die(current, die)
        else:
            self._table.remove_die(number, die)
        self.updater()

    def request_reset(self, *args):
        '''reset dice table'''
        self._table = ds.DiceTable()
        self.updater()

# kv file line NONE
class DiceCarouselApp(App):
    '''the app.  it's the dice platform'''
    def build(self):
        current_app = DicePlatform()

        return current_app

    def on_pause(self):
        return True
    def on_resume(self):
        pass

if __name__ == '__main__':
    RUNNING_APP = DiceCarouselApp()
    RUNNING_APP.run()

