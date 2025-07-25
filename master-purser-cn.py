import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import json
import math
import sys

# 商品列表
GOODS = [
    "实心弹", "葡萄弹", "链弹", "炸弹", "食物",
    "帆布", "木板", "砖头", "小麦", "衣物",
    "水果", "咖啡", "可可", "烟草", "糖",
    "棉花", "皮革", "乌木", "桃花心木", "香草",
    "椰仁", "红辣椒", "火药", "武器", "药品",
    "葡萄酒", "朗姆酒", "麦芽酒", "船用丝绸", "绳索",
    "铁木", "树脂", "奴隶", "黄金", "白银"
]

# 需求类型映射
DEMAND_TYPES = {
    "出口商品": 1,
    "普通商品": 2,
    "进口商品": 3,
    "热销商品": 4,
    "违禁品": 5
}
DEMAND_DISPLAY = {v: k for k, v in DEMAND_TYPES.items()}

# 商品属性
GOODS_PROPERTIES = {
    "实心弹": {"pack": 20, "pack_weight": 2},
    "葡萄弹": {"pack": 20, "pack_weight": 1},
    "链弹": {"pack": 20, "pack_weight": 2},
    "炸弹": {"pack": 20, "pack_weight": 3},
    "食物": {"pack": 10, "pack_weight": 1},
    "帆布": {"pack": 1, "pack_weight": 2},
    "木板": {"pack": 1, "pack_weight": 3},
    "砖头": {"pack": 10, "pack_weight": 6},
    "小麦": {"pack": 1, "pack_weight": 1},
    "衣物": {"pack": 10, "pack_weight": 1},
    "水果": {"pack": 1, "pack_weight": 1},
    "咖啡": {"pack": 1, "pack_weight": 2},
    "可可": {"pack": 1, "pack_weight": 2},
    "烟草": {"pack": 1, "pack_weight": 2},
    "糖": {"pack": 1, "pack_weight": 2},
    "棉花": {"pack": 1, "pack_weight": 1},
    "皮革": {"pack": 1, "pack_weight": 1},
    "乌木": {"pack": 1, "pack_weight": 5},
    "桃花心木": {"pack": 1, "pack_weight": 4},
    "香草": {"pack": 1, "pack_weight": 2},
    "椰仁": {"pack": 1, "pack_weight": 2},
    "红辣椒": {"pack": 1, "pack_weight": 2},
    "火药": {"pack": 20, "pack_weight": 1},
    "武器": {"pack": 10, "pack_weight": 1},
    "药品": {"pack": 30, "pack_weight": 1},
    "葡萄酒": {"pack": 1, "pack_weight": 2},
    "朗姆酒": {"pack": 1, "pack_weight": 1},
    "麦芽酒": {"pack": 1, "pack_weight": 1},
    "船用丝绸": {"pack": 1, "pack_weight": 2},
    "绳索": {"pack": 1, "pack_weight": 1},
    "铁木": {"pack": 1, "pack_weight": 7},
    "树脂": {"pack": 1, "pack_weight": 1},
    "奴隶": {"pack": 1, "pack_weight": 1},
    "黄金": {"pack": 1, "pack_weight": 2},
    "白银": {"pack": 1, "pack_weight": 1}
}

class MasterPurser:
    def __init__(self, root):
        self.root = root
        self.root.title("老伙计-值得信赖的贸易助理")
        self.root.geometry("1000x900")
        
        # 获取应用基础路径
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # 创建城市目录
        self.settlements_dir = os.path.join(base_path, "settlements-cn")
        os.makedirs(self.settlements_dir, exist_ok=True)
        
        # 设置笔记本
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # 创建标签页
        self.create_city_comparison_tab()
        self.create_selling_opportunities_tab()
        self.create_price_book_tab()
        self.create_profit_calculator_tab()
        
        # 初始状态
        self.purchase_list = []
        
    def create_city_comparison_tab(self):
        """城市比较标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="城市比较")
        
        # 配置网格权重
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
        
        # 城市选择
        ttk.Label(frame, text="起始城市:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.origin_var = tk.StringVar()
        self.origin_cb = ttk.Combobox(frame, textvariable=self.origin_var, state="readonly")
        self.origin_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.origin_var.trace_add("write", self.compare_cities)
        
        ttk.Label(frame, text="目标城市:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.dest_var = tk.StringVar()
        self.dest_cb = ttk.Combobox(frame, textvariable=self.dest_var, state="readonly")
        self.dest_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.dest_var.trace_add("write", self.compare_cities)
        
        # 刷新按钮
        ttk.Button(frame, text="刷新城市列表", command=self.populate_city_list).grid(row=2, column=0, columnspan=2, pady=5)
        
        # 隐藏违禁品选项
        self.hide_contraband_cc = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame, 
            text="隐藏违禁品", 
            variable=self.hide_contraband_cc,
            command=self.compare_cities
        ).grid(row=3, column=0, columnspan=2, pady=5)
        
        # 结果框架
        results_frame = ttk.LabelFrame(frame, text="有利可图的贸易机会")
        results_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 结果表格
        columns = ("商品", "起始需求", "目标需求", "利润潜力", "每包利润")
        self.results_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=15
        )
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.results_tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 配置列
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=120, anchor="center")
        
        self.results_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # 需求类型颜色
        self.results_tree.tag_configure('colonial', background='#ccffcc')  # 浅绿
        self.results_tree.tag_configure('normal', background='white')      # 白
        self.results_tree.tag_configure('imported', background='#cce6ff')  # 浅蓝
        self.results_tree.tag_configure('aggressive', background='#ffcc99') # 浅橙
        self.results_tree.tag_configure('contraband', background='#ffcccc') # 浅红
        
        # 初始填充
        self.populate_city_list()
    
    def create_selling_opportunities_tab(self):
        """销售机会标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="销售机会")
        
        # 配置网格权重
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
        
        # 城市选择
        ttk.Label(frame, text="起始城市:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.selling_origin_var = tk.StringVar()
        self.selling_origin_cb = ttk.Combobox(frame, textvariable=self.selling_origin_var, state="readonly")
        self.selling_origin_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.selling_origin_var.trace_add("write", self.update_selling_opportunities)
        
        # 商品选择
        ttk.Label(frame, text="选择商品:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.selected_good_var = tk.StringVar()
        self.good_cb = ttk.Combobox(frame, textvariable=self.selected_good_var, values=GOODS, state="readonly")
        self.good_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.selected_good_var.trace_add("write", self.update_selling_opportunities)
        
        # 刷新按钮
        ttk.Button(frame, text="刷新城市列表", command=self.populate_selling_city_list).grid(row=2, column=0, columnspan=2, pady=5)
        
        # 隐藏违禁品选项
        self.hide_contraband_so = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            frame, 
            text="隐藏违禁品", 
            variable=self.hide_contraband_so,
            command=self.update_selling_opportunities
        ).grid(row=3, column=0, columnspan=2, pady=5)
        
        # 结果框架
        results_frame = ttk.LabelFrame(frame, text="有利可图的销售城市")
        results_frame.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
        
        # 结果表格
        columns = ("城市", "需求", "利润潜力", "每包利润")
        self.selling_tree = ttk.Treeview(
            results_frame,
            columns=columns,
            show="headings",
            height=15
        )
        vsb = ttk.Scrollbar(results_frame, orient="vertical", command=self.selling_tree.yview)
        hsb = ttk.Scrollbar(results_frame, orient="horizontal", command=self.selling_tree.xview)
        self.selling_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # 配置列
        self.selling_tree.heading("城市", text="城市")
        self.selling_tree.heading("需求", text="需求类型")
        self.selling_tree.heading("利润潜力", text="利润潜力")
        self.selling_tree.heading("每包利润", text="每包利润")
        
        self.selling_tree.column("城市", width=150, anchor="w")
        self.selling_tree.column("需求", width=120, anchor="center")
        self.selling_tree.column("利润潜力", width=100, anchor="center")
        self.selling_tree.column("每包利润", width=100, anchor="center")
        
        self.selling_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # 需求类型颜色
        self.selling_tree.tag_configure('colonial', background='#ccffcc')  # 浅绿
        self.selling_tree.tag_configure('normal', background='white')      # 白
        self.selling_tree.tag_configure('imported', background='#cce6ff')  # 浅蓝
        self.selling_tree.tag_configure('aggressive', background='#ffcc99') # 浅橙
        self.selling_tree.tag_configure('contraband', background='#ffcccc') # 浅红
        
        # 初始填充
        self.populate_selling_city_list()
    
    def create_price_book_tab(self):
        """价格手册标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="价格手册")
        
        # 配置网格权重
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)
        
        # 城市名称输入
        city_frame = ttk.Frame(frame)
        city_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        
        ttk.Label(city_frame, text="城市名称:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.city_name = tk.StringVar()
        ttk.Entry(city_frame, textvariable=self.city_name, width=30).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # 商品需求框架
        goods_frame = ttk.LabelFrame(frame, text="商品价格设置")
        goods_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        goods_frame.columnconfigure(0, weight=1)
        goods_frame.rowconfigure(0, weight=1)
        
        # 创建滚动区域
        canvas = tk.Canvas(goods_frame)
        scrollbar = ttk.Scrollbar(goods_frame, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)
        
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 创建标题
        headers = ["商品", "需求类型", "收购价格", "出售价格", "可用数量"]
        for col, header in enumerate(headers):
            ttk.Label(self.scroll_frame, text=header, font=("TkDefaultFont", 9, "bold")).grid(
                row=0, column=col, padx=5, pady=2, sticky="w")
        
        # 创建需求条目
        self.demand_vars = {}
        self.purchase_price_vars = {}
        self.sell_price_vars = {}
        self.amount_vars = {}
        
        for row, good in enumerate(GOODS, start=1):
            # 商品名称
            ttk.Label(self.scroll_frame, text=good).grid(row=row, column=0, padx=5, pady=2, sticky="w")
            
            # 需求类型
            demand_var = tk.StringVar(value="普通商品")
            self.demand_vars[good] = demand_var
            demand_cb = ttk.Combobox(
                self.scroll_frame,
                textvariable=demand_var,
                values=list(DEMAND_TYPES.keys()),
                width=15,
                state="readonly"
            )
            demand_cb.grid(row=row, column=1, padx=5, pady=2)
            demand_var.trace_add("write", lambda *args, g=good: self.update_sell_price_state(g))
            
            # 收购价格
            purchase_price_var = tk.DoubleVar(value=0.0)
            self.purchase_price_vars[good] = purchase_price_var
            ttk.Entry(self.scroll_frame, textvariable=purchase_price_var, width=10).grid(
                row=row, column=2, padx=5, pady=2)
            
            # 出售价格
            sell_price_var = tk.DoubleVar(value=0.0)
            self.sell_price_vars[good] = sell_price_var
            sell_price_entry = ttk.Entry(self.scroll_frame, textvariable=sell_price_var, width=10)
            sell_price_entry.grid(row=row, column=3, padx=5, pady=2)
            
            # 可用数量
            amount_var = tk.IntVar(value=0)
            self.amount_vars[good] = amount_var
            ttk.Entry(self.scroll_frame, textvariable=amount_var, width=10).grid(
                row=row, column=4, padx=5, pady=2)
        
        # 按钮框架
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        ttk.Button(btn_frame, text="加载配置", command=self.load_price_book).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="保存配置", command=self.save_price_book).pack(side="left", padx=5)
    
    def update_sell_price_state(self, good):
        """根据需求类型更新销售价格状态"""
        demand = self.demand_vars[good].get()
        if demand == "违禁品":
            self.sell_price_vars[good].set(-1)
            for child in self.scroll_frame.winfo_children():
                if child.grid_info() and child.grid_info()["row"] == GOODS.index(good)+1 and child.grid_info()["column"] == 3:
                    child.configure(state="disabled")
        else:
            if self.sell_price_vars[good].get() == -1:
                self.sell_price_vars[good].set(0.0)
            for child in self.scroll_frame.winfo_children():
                if child.grid_info() and child.grid_info()["row"] == GOODS.index(good)+1 and child.grid_info()["column"] == 3:
                    child.configure(state="normal")
    
    def create_profit_calculator_tab(self):
        """利润计算器标签页"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="利润计算器")
        
        # 配置网格权重
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(4, weight=1)
        
        # 输入字段
        input_frame = ttk.LabelFrame(frame, text="交易参数")
        input_frame.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        input_frame.columnconfigure(1, weight=1)
        
        # 起始城市选择
        ttk.Label(input_frame, text="起始城市:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.calc_origin_var = tk.StringVar()
        self.calc_origin_cb = ttk.Combobox(input_frame, textvariable=self.calc_origin_var, state="readonly")
        self.calc_origin_cb.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        # 目标城市选择
        ttk.Label(input_frame, text="目标城市:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.calc_dest_var = tk.StringVar()
        self.calc_dest_cb = ttk.Combobox(input_frame, textvariable=self.calc_dest_var, state="readonly")
        self.calc_dest_cb.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        # 商品选择
        ttk.Label(input_frame, text="商品:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.calc_good_var = tk.StringVar()
        self.calc_good_cb = ttk.Combobox(input_frame, textvariable=self.calc_good_var, values=GOODS, state="readonly")
        self.calc_good_cb.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        
        # 购买数量
        ttk.Label(input_frame, text="购买数量:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.units_var = tk.IntVar(value=0)
        ttk.Entry(input_frame, textvariable=self.units_var).grid(row=3, column=1, padx=5, pady=5, sticky="ew")
        
        # 总可用百磅
        ttk.Label(input_frame, text="总可用百磅:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.total_centners_available_var = tk.DoubleVar(value=0.0)
        ttk.Entry(input_frame, textvariable=self.total_centners_available_var).grid(row=4, column=1, padx=5, pady=5, sticky="ew")
        
        # 按钮
        ttk.Button(input_frame, text="添加到购买列表", command=self.add_to_purchase_list).grid(
            row=5, column=0, columnspan=2, pady=10
        )
        ttk.Button(input_frame, text="最佳利润方案", command=self.calculate_best_plan).grid(
            row=6, column=0, columnspan=2, pady=5
        )
        
        # 购买列表
        list_frame = ttk.LabelFrame(frame, text="购买列表")
        list_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        columns = ("商品", "数量", "包数", "百磅", "成本", "收入", "利润")
        self.purchase_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            height=5
        )
        
        # 配置列
        for col in columns:
            self.purchase_tree.heading(col, text=col)
            self.purchase_tree.column(col, width=80, anchor="center")
        
        vsb = ttk.Scrollbar(list_frame, orient="vertical", command=self.purchase_tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient="horizontal", command=self.purchase_tree.xview)
        self.purchase_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.purchase_tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        # 移除按钮
        ttk.Button(frame, text="移除选中项", command=self.remove_selected_purchase).grid(
            row=2, column=0, columnspan=2, pady=5
        )
        
        # 摘要框架
        summary_frame = ttk.LabelFrame(frame, text="摘要")
        summary_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        summary_frame.columnconfigure(1, weight=1)
        summary_frame.columnconfigure(3, weight=1)
        
        # 摘要字段
        ttk.Label(summary_frame, text="总成本:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.total_cost_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.total_cost_var).grid(row=0, column=1, padx=5, pady=5, sticky="e")
        
        ttk.Label(summary_frame, text="总收入:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.total_revenue_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.total_revenue_var).grid(row=1, column=1, padx=5, pady=5, sticky="e")
        
        ttk.Label(summary_frame, text="总利润:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.total_profit_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.total_profit_var).grid(row=2, column=1, padx=5, pady=5, sticky="e")
        
        ttk.Label(summary_frame, text="总使用百磅:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.total_centners_used_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.total_centners_used_var).grid(row=0, column=3, padx=5, pady=5, sticky="e")
        
        ttk.Label(summary_frame, text="剩余百磅:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.remaining_centners_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.remaining_centners_var).grid(row=1, column=3, padx=5, pady=5, sticky="e")
        
        ttk.Label(summary_frame, text="每百磅利润:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
        self.profit_per_centner_var = tk.StringVar(value="0")
        ttk.Label(summary_frame, textvariable=self.profit_per_centner_var).grid(row=2, column=3, padx=5, pady=5, sticky="e")
        
        # 填充城市列表
        self.populate_profit_city_lists()
    
    def load_city_data(self, city_name):
        """加载城市数据，兼容旧格式"""
        file_path = os.path.join(self.settlements_dir, f"{city_name}.json")
        try:
            # 确保文件存在
            if not os.path.exists(file_path):
                return None
                
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否是旧格式（商品: 需求值）
            if any(isinstance(v, int) for v in data.values()):
                # 转换为新格式
                new_data = {}
                for good, value in data.items():
                    if isinstance(value, int):
                        new_data[good] = {
                            "demand": value,
                            "purchase_price": 0.0,
                            "sell_price": -1 if value == 5 else 0.0,
                            "amount": 0
                        }
                    else:
                        new_data[good] = value
                return new_data
            return data
        except Exception as e:
            print(f"加载城市数据错误: {str(e)}")
            return None
    
    def populate_city_list(self):
        """填充城市比较的城市列表"""
        try:
            # 确保目录存在
            os.makedirs(self.settlements_dir, exist_ok=True)
            
            # 获取目录中的JSON文件
            cities = [f[:-5] for f in os.listdir(self.settlements_dir) 
                      if f.endswith(".json") and os.path.isfile(os.path.join(self.settlements_dir, f))]
        except Exception as e:
            print(f"加载城市列表错误: {str(e)}")
            cities = []
            
        self.origin_cb["values"] = cities
        self.dest_cb["values"] = cities
        
        if cities:
            self.origin_var.set(cities[0])
            if len(cities) > 1:
                self.dest_var.set(cities[1])
    
    def populate_selling_city_list(self):
        """填充销售机会的城市列表"""
        try:
            os.makedirs(self.settlements_dir, exist_ok=True)
            cities = [f[:-5] for f in os.listdir(self.settlements_dir) 
                      if f.endswith(".json") and os.path.isfile(os.path.join(self.settlements_dir, f))]
        except Exception as e:
            print(f"加载销售城市列表错误: {str(e)}")
            cities = []
            
        cities.insert(0, "海上")
        self.selling_origin_cb["values"] = cities
        
        if cities:
            self.selling_origin_var.set(cities[0])
    
    def populate_profit_city_lists(self):
        """填充利润计算器的城市列表"""
        try:
            os.makedirs(self.settlements_dir, exist_ok=True)
            cities = [f[:-5] for f in os.listdir(self.settlements_dir) 
                      if f.endswith(".json") and os.path.isfile(os.path.join(self.settlements_dir, f))]
        except Exception as e:
            print(f"加载利润计算器城市列表错误: {str(e)}")
            cities = []
            
        self.calc_origin_cb["values"] = cities
        self.calc_dest_cb["values"] = cities
        
        if cities:
            self.calc_origin_var.set(cities[0])
            if len(cities) > 1:
                self.calc_dest_var.set(cities[1])
    
    def save_price_book(self):
        """保存城市价格手册"""
        city_name = self.city_name.get().strip()
        if not city_name:
            messagebox.showerror("错误", "请输入城市名称")
            return
        
        price_book = {}
        for good in GOODS:
            demand_text = self.demand_vars[good].get()
            demand_value = DEMAND_TYPES.get(demand_text, 2)  # 默认普通商品
            
            purchase_price = self.purchase_price_vars[good].get()
            sell_price = self.sell_price_vars[good].get()
            amount = self.amount_vars[good].get()
            
            # 违禁品特殊处理
            if demand_value == 5:  # 违禁品
                sell_price = -1
            
            price_book[good] = {
                "demand": demand_value,
                "purchase_price": purchase_price,
                "sell_price": sell_price,
                "amount": amount
            }
        
        filename = os.path.join(self.settlements_dir, f"{city_name}.json")
        try:
            with open(filename, "w", encoding='utf-8') as f:
                json.dump(price_book, f, indent=2, ensure_ascii=False)
        except Exception as e:
            messagebox.showerror("错误", f"保存失败: {str(e)}")
            return
        
        # 重置UI
        self.city_name.set("")
        for good in GOODS:
            self.demand_vars[good].set("普通商品")
            self.purchase_price_vars[good].set(0.0)
            self.sell_price_vars[good].set(0.0)
            self.amount_vars[good].set(0)
        
        messagebox.showinfo("成功", f"{city_name}的配置已保存")
        self.populate_city_list()
        self.populate_selling_city_list()
        self.populate_profit_city_lists()
    
    def load_price_book(self):
        """加载城市价格手册"""
        filename = filedialog.askopenfilename(
            initialdir=self.settlements_dir,
            filetypes=[("JSON文件", "*.json")]
        )
        if not filename:
            return
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                price_book = json.load(f)
            
            city_name = os.path.basename(filename)[:-5]
            self.city_name.set(city_name)
            
            for good in GOODS:
                if good in price_book:
                    good_data = price_book[good]
                    
                    # 处理新旧格式
                    if isinstance(good_data, dict):
                        # 新格式
                        demand_value = good_data.get("demand", 2)
                        purchase_price = good_data.get("purchase_price", 0.0)
                        sell_price = good_data.get("sell_price", 0.0)
                        amount = good_data.get("amount", 0)
                    else:
                        # 旧格式（整数）
                        demand_value = good_data
                        purchase_price = 0.0
                        sell_price = -1 if demand_value == 5 else 0.0
                        amount = 0
                    
                    # 设置需求类型
                    demand_text = DEMAND_DISPLAY.get(demand_value, "普通商品")
                    self.demand_vars[good].set(demand_text)
                    
                    # 设置价格和数量
                    self.purchase_price_vars[good].set(purchase_price)
                    self.sell_price_vars[good].set(sell_price)
                    self.amount_vars[good].set(amount)
                    
                    # 更新销售价格状态
                    if demand_value == 5:  # 违禁品
                        for child in self.scroll_frame.winfo_children():
                            if child.grid_info() and child.grid_info()["row"] == GOODS.index(good)+1 and child.grid_info()["column"] == 3:
                                child.configure(state="disabled")
                    else:
                        for child in self.scroll_frame.winfo_children():
                            if child.grid_info() and child.grid_info()["row"] == GOODS.index(good)+1 and child.grid_info()["column"] == 3:
                                child.configure(state="normal")
        except Exception as e:
            messagebox.showerror("错误", f"加载配置失败:\n{str(e)}")
    
    def compare_cities(self, *args):
        """比较起始和目标城市以寻找有利可图的交易"""
        origin = self.origin_var.get()
        dest = self.dest_var.get()
        
        # 验证选择
        if not origin or not dest:
            return
        
        if origin == dest:
            # 清除结果
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            return
        
        try:
            # 加载配置
            origin_config = self.load_city_data(origin)
            dest_config = self.load_city_data(dest)
            
            if origin_config is None or dest_config is None:
                messagebox.showerror("错误", "加载城市数据失败")
                return
            
            # 清除先前结果
            for item in self.results_tree.get_children():
                self.results_tree.delete(item)
            
            # 寻找有利可图的商品
            profitable_goods = []
            for good in GOODS:
                # 获取起始数据
                origin_good_data = origin_config.get(good, {})
                origin_demand = origin_good_data.get("demand", 2)
                origin_sell_price = origin_good_data.get("sell_price", 0.0)
                
                # 获取目标数据
                dest_good_data = dest_config.get(good, {})
                dest_demand = dest_good_data.get("demand", 2)
                dest_purchase_price = dest_good_data.get("purchase_price", 0.0)
                
                # 隐藏违禁品处理
                if self.hide_contraband_cc.get() and dest_demand == 5:
                    continue
                
                if dest_demand > origin_demand:
                    profit = dest_demand - origin_demand
                    origin_text = DEMAND_DISPLAY.get(origin_demand, "未知")
                    dest_text = DEMAND_DISPLAY.get(dest_demand, "未知")
                    
                    # 计算每包利润
                    if origin_sell_price > 0 and dest_purchase_price > 0 and dest_demand != 5:
                        profit_per_pack = dest_purchase_price - origin_sell_price
                        profit_per_pack_str = f"{profit_per_pack:.2f}"
                    else:
                        profit_per_pack_str = "???"
                    
                    profitable_goods.append((good, origin_text, dest_text, profit, dest_demand, profit_per_pack_str))
            
            # 按利润降序排序
            profitable_goods.sort(key=lambda x: x[3], reverse=True)
            
            # 添加到结果树
            for good, origin_disp, dest_disp, profit, dest_value, profit_per_pack in profitable_goods:
                # 基于目标需求类型的颜色编码
                if dest_value == 1:  # 出口商品
                    tag = 'colonial'
                elif dest_value == 2:  # 普通商品
                    tag = 'normal'
                elif dest_value == 3:  # 进口商品
                    tag = 'imported'
                elif dest_value == 4:  # 热销商品
                    tag = 'aggressive'
                elif dest_value == 5:  # 违禁品
                    tag = 'contraband'
                else:
                    tag = ''  # 默认无颜色
                
                self.results_tree.insert("", "end", values=(
                    good,
                    origin_disp,
                    dest_disp,
                    f"+{profit}",
                    profit_per_pack
                ), tags=(tag,))
                
        except Exception as e:
            messagebox.showerror("错误", f"比较城市失败:\n{str(e)}")
    
    def update_selling_opportunities(self, *args):
        """更新选定商品的销售机会"""
        origin = self.selling_origin_var.get()
        good = self.selected_good_var.get()
        
        # 验证选择
        if not origin or not good:
            return
        
        try:
            # 处理"海上"起始点
            if origin == "海上":
                origin_demand = 0
                origin_text = "海上(免费)"
                origin_sell_price = 0  # 免费获取
            else:
                # 加载起始配置
                origin_config = self.load_city_data(origin)
                if origin_config is None:
                    messagebox.showerror("错误", f"无法加载{origin}的数据")
                    return
                    
                origin_good_data = origin_config.get(good, {})
                origin_demand = origin_good_data.get("demand", 2)
                origin_text = DEMAND_DISPLAY.get(origin_demand, "未知")
                origin_sell_price = origin_good_data.get("sell_price", 0.0)
            
            # 清除先前结果
            for item in self.selling_tree.get_children():
                self.selling_tree.delete(item)
            
            # 寻找有利可图的城市
            profitable_cities = []
            for city_file in os.listdir(self.settlements_dir):
                if city_file.endswith(".json"):
                    city_name = city_file[:-5]
                    # 跳过自身比较
                    if origin != "海上" and city_name == origin:
                        continue
                    
                    city_config = self.load_city_data(city_name)
                    if city_config is None:
                        continue
                    
                    city_good_data = city_config.get(good, {})
                    city_demand = city_good_data.get("demand", 2)
                    city_purchase_price = city_good_data.get("purchase_price", 0.0)
                    
                    # 隐藏违禁品处理
                    if self.hide_contraband_so.get() and city_demand == 5:
                        continue
                    
                    # 当起始点是"海上"时始终显示城市
                    if origin == "海上" or city_demand > origin_demand:
                        profit = city_demand - origin_demand
                        demand_text = DEMAND_DISPLAY.get(city_demand, "未知")
                        
                        # 计算每包利润
                        if origin_sell_price >= 0 and city_purchase_price > 0 and city_demand != 5:
                            profit_per_pack = city_purchase_price - origin_sell_price
                            profit_per_pack_str = f"{profit_per_pack:.2f}"
                        else:
                            profit_per_pack_str = "???"
                        
                        profitable_cities.append((city_name, demand_text, profit, city_demand, profit_per_pack_str))
            
            # 按利润降序排序
            profitable_cities.sort(key=lambda x: x[2], reverse=True)
            
            # 添加到结果树
            for city, demand_text, profit, demand_value, profit_per_pack in profitable_cities:
                # 基于目标需求类型的颜色编码
                if demand_value == 1:  # 出口商品
                    tag = 'colonial'
                elif demand_value == 2:  # 普通商品
                    tag = 'normal'
                elif demand_value == 3:  # 进口商品
                    tag = 'imported'
                elif demand_value == 4:  # 热销商品
                    tag = 'aggressive'
                elif demand_value == 5:  # 违禁品
                    tag = 'contraband'
                else:
                    tag = ''  # 默认无颜色
                
                self.selling_tree.insert("", "end", values=(
                    city,
                    demand_text,
                    f"+{profit}",
                    profit_per_pack
                ), tags=(tag,))
            
            if not profitable_cities:
                self.selling_tree.insert("", "end", values=(
                    "未找到有利可图的城市", 
                    f"当前需求: {origin_text}",
                    "",
                    ""
                ))
                
        except Exception as e:
            messagebox.showerror("错误", f"寻找销售机会失败:\n{str(e)}")
    
    def add_to_purchase_list(self):
        """将当前交易添加到购买列表"""
        good = self.calc_good_var.get()
        units = self.units_var.get()
        total_available = self.total_centners_available_var.get()
        
        # 验证输入
        if not good:
            messagebox.showerror("错误", "请选择商品")
            return
        if units <= 0:
            messagebox.showerror("错误", "数量必须大于零")
            return
        if total_available <= 0:
            messagebox.showerror("错误", "总可用百磅必须为正数")
            return
        
        # 获取包装属性
        pack_size = GOODS_PROPERTIES[good]["pack"]
        pack_weight = GOODS_PROPERTIES[good]["pack_weight"]
        
        # 计算包数（向上取整）
        packs = math.ceil(units / pack_size)
        # 计算占用的百磅数
        item_centners = packs * pack_weight
        
        # 计算当前总使用百磅数
        current_total_used = self.get_total_centners_used()
        
        # 检查空间
        if current_total_used + item_centners > total_available:
            messagebox.showerror("错误", "百磅空间不足")
            return
        
        # 获取起始城市价格
        origin = self.calc_origin_var.get()
        if origin == "海上":
            purchase_price = 0.0  # 海上免费
        else:
            origin_config = self.load_city_data(origin)
            if origin_config is None:
                messagebox.showerror("错误", f"无法加载{origin}的数据")
                return
            origin_good_data = origin_config.get(good, {})
            purchase_price = origin_good_data.get("purchase_price", 0.0)
        
        # 获取目标城市价格
        destination = self.calc_dest_var.get()
        dest_config = self.load_city_data(destination)
        if dest_config is None:
            messagebox.showerror("错误", f"无法加载{destination}的数据")
            return
        dest_good_data = dest_config.get(good, {})
        dest_demand = dest_good_data.get("demand", 2)
        sell_price = dest_good_data.get("purchase_price", 0.0)
        
        # 违禁品特殊处理
        if dest_demand == 5:
            sell_price = 0.0
        
        # 计算成本、收入和利润
        cost = packs * purchase_price
        revenue = packs * sell_price
        profit = revenue - cost
        
        # 添加到购买列表
        item = {
            "good": good,
            "units": units,
            "packs": packs,
            "centners": item_centners,
            "purchase_price": purchase_price,
            "selling_price": sell_price,
            "cost": cost,
            "revenue": revenue,
            "profit": profit
        }
        self.purchase_list.append(item)
        
        # 添加到树状图
        self.purchase_tree.insert("", "end", values=(
            good,
            units,
            packs,
            item_centners,
            f"{cost:.2f}",
            f"{revenue:.2f}",
            f"{profit:.2f}"
        ))
        
        # 更新摘要
        self.update_summary()
    
    def get_total_centners_used(self):
        """计算购买列表使用的总百磅数"""
        return sum(item['centners'] for item in self.purchase_list)
    
    def remove_selected_purchase(self):
        """从购买列表中移除选定项"""
        selected = self.purchase_tree.selection()
        if not selected:
            return
        
        # 获取选定项的索引
        index = self.purchase_tree.index(selected[0])
        
        # 从树状图中移除
        self.purchase_tree.delete(selected[0])
        
        # 从购买列表中移除
        self.purchase_list.pop(index)
        
        # 更新摘要
        self.update_summary()
    
    def update_summary(self):
        """更新摘要信息"""
        total_cost = 0
        total_revenue = 0
        total_centners_used = self.get_total_centners_used()
        total_available = self.total_centners_available_var.get()
        
        for item in self.purchase_list:
            total_cost += item["cost"]
            total_revenue += item["revenue"]
        
        total_profit = total_revenue - total_cost
        remaining_centners = total_available - total_centners_used
        
        if total_centners_used > 0:
            profit_per_centner = total_profit / total_centners_used
        else:
            profit_per_centner = 0
        
        # 更新变量
        self.total_cost_var.set(f"{total_cost:.2f}")
        self.total_revenue_var.set(f"{total_revenue:.2f}")
        self.total_profit_var.set(f"{total_profit:.2f}")
        self.total_centners_used_var.set(f"{total_centners_used:.1f}")
        self.remaining_centners_var.set(f"{remaining_centners:.1f}")
        self.profit_per_centner_var.set(f"{profit_per_centner:.2f}")

    def calculate_best_plan(self):
        """Calculate the best profit plan based on known prices, availability, and capital"""
        origin = self.calc_origin_var.get()
        destination = self.calc_dest_var.get()
        total_centners = self.total_centners_available_var.get()
        current_capital = self.capital_var.get()
        
        if not origin or not destination:
            messagebox.showerror("错误", "请选择起始和目标城市")
            return
        if total_centners <= 0:
            messagebox.showerror("错误", "可用百磅数应为正数")
            return
        if current_capital <= 0:
            messagebox.showerror("错误", "当前资本应为正数")
            return
        
        # Load origin city data
        origin_data = self.load_city_data(origin)
        if origin_data is None:
            messagebox.showerror("错误", f"无法加载{origin}数据")
            return
        
        # Load destination city data
        dest_data = self.load_city_data(destination)
        if dest_data is None:
            messagebox.showerror("错误", f"无法加载{destination}数据")
            return
        
        # Clear current purchase list
        self.purchase_list = []
        for item in self.purchase_tree.get_children():
            self.purchase_tree.delete(item)
        
        # Find profitable goods
        profitable_goods = []
        for good in GOODS:
            # Get destination demand
            dest_good_data = dest_data.get(good, {})
            dest_demand = dest_good_data.get("demand", 2)
            
            # Skip if contraband at destination
            if dest_demand == 5:
                continue
            
            # Get origin price and availability
            origin_good_data = origin_data.get(good, {})
            purchase_price = origin_good_data.get("purchase_price", 0.0)
            available_units = origin_good_data.get("amount", 0)
                
            # Skip if price unknown or no availability
            if purchase_price <= 0 or available_units <= 0:
                continue
            
            # Get destination selling price
            sell_price = dest_good_data.get("purchase_price", 0.0)
            if sell_price <= 0:
                continue
            
            # Calculate profit per pack
            profit_per_pack = sell_price - purchase_price
            if profit_per_pack <= 0:
                continue
            
            # Get pack properties
            pack_size = GOODS_PROPERTIES[good]["pack"]
            pack_weight = GOODS_PROPERTIES[good]["pack_weight"]
            
            # Calculate max packs available
            max_packs = min(available_units // pack_size, 
                            total_centners // pack_weight)
            
            if max_packs > 0:
                # Calculate profit per centner for sorting
                profit_per_centner = profit_per_pack / pack_weight
                profitable_goods.append({
                    "good": good,
                    "profit_per_centner": profit_per_centner,
                    "profit_per_pack": profit_per_pack,
                    "pack_size": pack_size,
                    "pack_weight": pack_weight,
                    "max_packs": max_packs,
                    "purchase_price": purchase_price,
                    "sell_price": sell_price
                })
        
        # Sort by profit per centner (descending)
        profitable_goods.sort(key=lambda x: x["profit_per_centner"], reverse=True)
        
        # Allocate centners and capital
        remaining_centners = total_centners
        remaining_capital = current_capital
        purchase_plan = []
        
        for item in profitable_goods:
            if remaining_centners <= 0 or remaining_capital <= 0:
                break
            
            # Calculate how many packs we can take based on centners and capital
            max_by_centners = remaining_centners // item["pack_weight"]
            max_by_capital = remaining_capital // item["purchase_price"] if item["purchase_price"] > 0 else float('inf')
            
            packs = min(item["max_packs"], max_by_centners, max_by_capital)
            packs = int(packs)  # Ensure whole number
            
            if packs <= 0:
                continue
            
            # Calculate details
            units = packs * item["pack_size"]
            centners = packs * item["pack_weight"]
            cost = packs * item["purchase_price"]
            revenue = packs * item["sell_price"]
            profit = revenue - cost
            
            # Add to purchase plan
            purchase_plan.append({
                "good": item["good"],
                "units": units,
                "packs": packs,
                "centners": centners,
                "purchase_price": item["purchase_price"],
                "selling_price": item["sell_price"],
                "cost": cost,
                "revenue": revenue,
                "profit": profit
            })
            
            # Update remaining resources
            remaining_centners -= centners
            remaining_capital -= cost
        
        # Add to purchase list
        for item in purchase_plan:
            self.purchase_list.append(item)
            self.purchase_tree.insert("", "end", values=(
                item["good"],
                item["units"],
                item["packs"],
                item["centners"],
                f"{item['cost']:.2f}",
                f"{item['revenue']:.2f}",
                f"{item['profit']:.2f}"
            ))
        
        # Update summary
        self.update_summary()
        
        if not purchase_plan:
            messagebox.showinfo("最佳方案", "未找到有利可图的交易方案")
        else:
            messagebox.showinfo("最佳方案", "已计算最优利润方案")

if __name__ == "__main__":
    root = tk.Tk()
    app = MasterPurser(root)
    root.mainloop()