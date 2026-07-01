#!/usr/bin/env python3
"""为 system-tree.json 中所有中间物相节点补充第一性原理分析数据。

用法: python scripts/add_first_principles.py [--dry-run]
"""

import json
import sys
from pathlib import Path
from copy import deepcopy

ROOT = Path(__file__).resolve().parent.parent
TREE_PATH = ROOT / "system-tree.json"

# ============================================================
# 第一性原理分析数据 — 按节点 ID 索引
# ============================================================
FIRST_PRINCIPLES_DATA = {
    # ===== raw_black_talc: 黑滑石原矿 =====
    "raw_black_talc": {
        "structure_summary": {
            "property": "第一性原理 · 晶体结构",
            "value": "2:1型 (T-O-T) 层状硅酸盐，三斜晶系 P1。单层结构：SiO₄ 四面体片(T)—Mg(O,OH)₆ 八面体片(O)—SiO₄ 四面体片(T)，TOT 层间以 van der Waals 力 + 类石墨烯碳层 (sp² C-C) 结合，层间距 d(001)≈0.94 nm",
            "type": "first_principles_insight"
        },
        "bond_analysis": {
            "property": "第一性原理 · 化学键分析",
            "value": "层内 Si-O 共价键 (键能 ~466 kJ/mol, 电负性差 1.54)→结构刚性骨架；Mg-O 离子键 (电负性差 2.13)→八面体层柔韧、易选择性溶解；层间 van der Waals + C-C sp² π 键 (层间碳层)→极低层间剪切强度→莫氏硬度仅 1",
            "type": "first_principles_insight"
        },
        "structure_to_properties": {
            "property": "第一性原理 · 结构→性质推导",
            "value": "① 层间弱键→易层间滑移→天然润滑性+低硬度→超细粉碎低成本(天然纳米级)。② TOT 层含 OH→800°C+脱羟基→层状结构崩塌→非晶化+新物相(顽火辉石)。③ Mg-O 八面体层 vs Si-O 四面体层键强差异→酸浸时 Mg 优先溶出而 Si 骨架保留→选择性分离 Mg/Si。④ 层间 sp² 碳→类石墨烯层内 π 电子离域→潜在导电性",
            "type": "first_principles_insight"
        },
        "derived_possibilities": {
            "property": "第一性原理 · 推导可能新性质",
            "value": "① TOT 层间空间(~0.94 nm 层间距)→可插层化学(Li⁺/Na⁺等离子插层)→潜在电池电极材料或离子交换剂。② 层间碳层 sp² 结构→N₂气氛下可石墨化为类石墨烯→导电/导热功能相。③ SiO₄ 四面体片可剥离为二维纳米片(类蒙脱石)→纳米填料增强聚合物/阻隔材料。④ TOT 层天然限域空间→原位合成纳米颗粒(量子点/催化金属)→限域催化",
            "type": "first_principles_insight"
        }
    },

    # ===== enstatite_from_talc: 顽火辉石 =====
    "enstatite_from_talc": {
        "structure_summary": {
            "property": "第一性原理 · 晶体结构",
            "value": "正交晶系 Pbca (proto-MgSiO₃ 为 P2₁/c), 链状硅酸盐(辉石族)。SiO₄ 四面体共角顶形成沿 c 轴延伸的单链 [SiO₃]²⁻，链间由 MgO₆ 八面体连接。Mg²⁺ 占据 M1 和 M2 两种八面体位(M1 较规则, M2 扭曲稍大)。晶胞参数 a≈18.23Å, b≈8.81Å, c≈5.18Å",
            "type": "first_principles_insight"
        },
        "bond_analysis": {
            "property": "第一性原理 · 化学键分析",
            "value": "Si-O 共价键(键能 ~466 kJ/mol)→刚性四面体链骨架，决定低极化率；Mg-O 离子键→八面体层提供结构连接但贡献极化。电负性：Si(1.90) vs O(3.44)→Si-O 差 1.54(共价为主); Mg(1.31) vs O→差 2.13(离子为主)。Mg-O 键强较弱(~167 kJ/mol)，是热膨胀和离子取代的主要位点",
            "type": "first_principles_insight"
        },
        "structure_to_properties": {
            "property": "第一性原理 · 结构→性质推导",
            "value": "【εr≈5-7 低】Si-O 共价四面体链→电子被紧束缚→低离子极化率→Clausius-Mossotti 关系给出 εr≈5-7(实验 5.11 PAPER-004)。【Q×f 高 >100,000 GHz】刚性共价链 + 轻重原子质量差大(Si 28 vs Mg 24 vs O 16)→声子频谱展宽小→非谐声子散射弱→本征介电损耗极低→Q×f 可达 145,846(PAPER-011)。【τf<0 负值】Mg-O 离子键热膨胀→MgO₆ 八面体体积↑→键长↑→单位体积极化率↓→τf≈−17~−19 ppm/°C。【polymorphism 相变】proto→ortho 相变源于 MgO₆ 扭曲+SiO₄ 链旋转→降温过程产生微裂纹→Q×f 劣化(PAPER-010 Cu²⁺ 抑制此相变)",
            "type": "first_principles_insight"
        },
        "derived_possibilities": {
            "property": "第一性原理 · 推导可能新性质",
            "value": "① 链状 SiO₄ 结构→强各向异性热膨胀(链向 vs 链间不同)→可设计定向热管理材料或应力缓冲层。② 宽能隙(~7 eV, DFT 计算)→紫外透明窗口(200-300 nm)→UV-LED 封装或光学窗口。③ Mg²⁺ 可被过渡金属(TM⁺²)取代→八面体位掺杂(TM-O₆)→调控磁性/荧光/催化→可能用于发光材料(Mn⁴⁺ 红色荧光粉)、催化剂载体。④ 链状结构较层状更开放→潜在离子导体(Mg²⁺ 沿链迁移)→固态电解质？⑤ 低 εr+低损耗→不仅微波介质，也可作为高频 PCB 基板填料",
            "type": "first_principles_insight"
        }
    },

    # ===== forsterite_from_talc: 镁橄榄石 =====
    "forsterite_from_talc": {
        "structure_summary": {
            "property": "第一性原理 · 晶体结构",
            "value": "正交晶系 Pbnm (Olivine 结构)，孤立 SiO₄ 四面体被 MgO₆ 八面体包围。Mg²⁺ 占据 M1(反演中心, 较规则八面体)和 M2(镜面对称, 较扭曲八面体)两体位。O²⁻ 近似六方密堆积(hcp)，Si⁴⁺ 占据 1/8 四面体空隙，Mg²⁺ 占据 1/2 八面体空隙。晶胞参数 a≈4.75Å, b≈10.20Å, c≈5.98Å",
            "type": "first_principles_insight"
        },
        "bond_analysis": {
            "property": "第一性原理 · 化学键分析",
            "value": "孤立 SiO₄→无四面体间桥氧→四面体不共享顶点→极度刚性(无链/层变形自由度)；Mg-O 离子键(M1: 键长 2.07-2.10Å, M2: 键长 2.03-2.13Å)→八面体提供 3D 连接但本身柔韧。Si-O 键(~466 kJ/mol)远强于 Mg-O(~167 kJ/mol)→孤立 SiO₄ 为'刚性岛'嵌入 Mg-O 离子'海洋'→整体晶格刚性极高",
            "type": "first_principles_insight"
        },
        "structure_to_properties": {
            "property": "第一性原理 · 结构→性质推导",
            "value": "【Q×f=270,000 GHz 极高 PAPER-018】孤立 SiO₄→无四面体链/环变形→极度低非谐性→本征声子散射极弱→Q×f 为所有硅酸盐中最高之一。【εr=6.8】SiO₄ 孤立→无离子协同极化→仅 Mg-O 对和 Si-O 键贡献极化→中等偏低介电常数。【低热导 3.6→1.68 W/m·K PAPER-019】复杂晶体结构(Z=4/晶胞, 28 atoms)→声子频谱复杂+轻重原子质量差大(Si 28 vs Mg 24)→低声子群速度+强Umklapp散射→热导比8YSZ低~20%。【高熔点 1890°C】孤立 SiO₄+紧密氧堆积→高晶格能→难熔。【热膨胀 CTE 8.6-11.3×10⁻⁶/K】离子键 Mg-O 主导热膨胀(非 Si-O 共价)→CTE 偏大但可控",
            "type": "first_principles_insight"
        },
        "derived_possibilities": {
            "property": "第一性原理 · 推导可能新性质",
            "value": "① Cr⁴⁺/Mn⁴⁺ 可取代 Si⁴⁺(四面体位)或 Mg²⁺(八面体位)→d-d 电子跃迁→可调谐近红外激光晶体(Cr:forsterite 已是商用激光晶体 1.1-1.3μm)。② Mg²⁺+Si⁴⁺ 均是生物必需元素→镁橄榄石具有本征生物相容性和生物可降解性→骨组织工程支架(已有个别研究 PAPER-002 提及)。③ 低热导+高熔点+良好热稳定性→热障涂层(TBC)理想候选(已由 PAPER-019 验证 >830 次循环)。④ 孤立 SiO₄→无链/层各向异性→3D 各向同性机械性能→优于链状顽火辉石。⑤ 两个独立八面体位 M1/M2→可选择性掺杂不同离子到不同位→多色荧光或双功能材料",
            "type": "first_principles_insight"
        }
    },

    # ===== separated_mgo: 高纯 MgO =====
    "separated_mgo": {
        "structure_summary": {
            "property": "第一性原理 · 晶体结构",
            "value": "立方晶系 Fm3̄m (岩盐/NaCl 结构)，Mg²⁺ 和 O²⁻ 均为六配位(八面体配位)，晶胞参数 a≈4.21Å。高度对称结构→各向同性物理性质",
            "type": "first_principles_insight"
        },
        "bond_analysis": {
            "property": "第一性原理 · 化学键分析",
            "value": "纯离子键：Mg²⁺(r=0.72Å) + O²⁻(r=1.40Å)，电负性差 2.13(Pauling)→离子性 ~63%。强 Madelung 能→高晶格能(3795 kJ/mol)→极高熔点 2852°C",
            "type": "first_principles_insight"
        },
        "structure_to_properties": {
            "property": "第一性原理 · 结构→性质推导",
            "value": "【宽能隙 ~7.8 eV (DFT GW 计算)】纯离子键→满价带(O 2p)+空导带(Mg 3s)→大能隙→绝缘体、紫外透明。【高熔点 2852°C】强 Madelung 能+紧密离子堆积→高晶格能→优异耐火材料。【碱性与催化】表面 O²⁻ 离子→Lewis 碱位→可催化 aldol 缩合等碱催化反应。【MgO 酸溶】离子键→极性溶剂(H₂O/H⁺)攻击→Mg²⁺ 水合释出(PAPER-007 验证→97.98% 浸出率)",
            "type": "first_principles_insight"
        },
        "derived_possibilities": {
            "property": "第一性原理 · 推导可能新性质",
            "value": "① 宽能隙+低介电常数(~9.8)→良好绝缘栅介质→薄膜晶体管(TFT)栅极绝缘层候选。② 表面 O²⁻ Lewis 碱性+Mg²⁺ Lewis 酸性→双功能催化→CO₂ 吸附/转化(形成 MgCO₃)。③ 纳米 MgO→高比表面+丰富表面缺陷(F-center)→抗菌/光催化(已有研究)。④ 隧道势垒：MgO(001)能隙大→自旋电子学中 MTJ (磁隧道结)标准势垒材料。⑤ 岩盐结构→与 FeO, CoO, NiO 晶格匹配→可外延生长异质结构",
            "type": "first_principles_insight"
        }
    },

    # ===== separated_sio2: 高纯 SiO₂ =====
    "separated_sio2": {
        "structure_summary": {
            "property": "第一性原理 · 晶体结构",
            "value": "酸浸残渣 SiO₂ 以无定形为主(部分方石英微晶)。无定形 SiO₂: 连续随机网络(CRN), 每个 Si 四配位 O, 每个 O 桥接 2 个 Si (Q⁴/Q³ 分布)。方石英: 四方晶系 P4₁2₁2 或立方 Fd3̄m, SiO₄ 四面体共角顶形成类似金刚石的三维网络",
            "type": "first_principles_insight"
        },
        "bond_analysis": {
            "property": "第一性原理 · 化学键分析",
            "value": "Si-O 共价键为主(键能 ~466 kJ/mol, 电负性差 1.54)→约 50% 离子性+50% 共价性。Si-O-Si 桥键角 ~144°(无定形分布 120-180°)→连续三维共价网络→化学稳定性极高(HF 除外)",
            "type": "first_principles_insight"
        },
        "structure_to_properties": {
            "property": "第一性原理 · 结构→性质推导",
            "value": "【低 εr ~3.8(无定形), 4.4(方石英)】Si-O 共价键→低极化率+无偶极矩→最低介电常数之一→CMOS 器件关键介质(非本体系但物理本质相通)。【高化学稳定性→仅 HF 能攻击 Si-O-Si 桥键→PAPER-007 中 δ-MgO 过程依赖 HF 破解 Si-O 网络】【高比表面(纳米 SiO₂)→酸浸残渣多孔→可用作吸附剂/催化剂载体】【绝缘→宽能隙 ~9 eV→深紫外透明】",
            "type": "first_principles_insight"
        },
        "derived_possibilities": {
            "property": "第一性原理 · 推导可能新性质",
            "value": "① 无定形 SiO₂→高比表面+表面 Si-OH 基团→功能化接枝(硅烷偶联剂)→填料增强、色谱固定相。② 纳米 SiO₂→低折射率(~1.46)+低 εr→光学减反膜、低介电介质层。③ 多孔 SiO₂(酸浸残渣)→天然多孔模板→限域合成纳米材料(分子筛前驱体)。④ 方石英→负热膨胀相变(α↔β 在 ~270°C)→可设计零膨胀复合材料(与正膨胀相复合)。⑤ SiO₂ 微球→光子晶体结构单元→结构色/光学传感",
            "type": "first_principles_insight"
        }
    },

    # ===== graphitized_carbon: 石墨化碳 =====
    "graphitized_carbon": {
        "structure_summary": {
            "property": "第一性原理 · 晶体结构",
            "value": "类石墨烯层状结构：sp² 杂化碳六元环二维网络，层内 C-C 键长 ~1.42Å(石墨烯本征)，层间距 d(002)≈0.335-0.340 nm(N₂气氛高温石墨化后接近理想石墨 d=0.3354 nm)。存在 C-O 杂键缺陷(碳层边缘/面内氧化位点)→非完美石墨烯",
            "type": "first_principles_insight"
        },
        "bond_analysis": {
            "property": "第一性原理 · 化学键分析",
            "value": "层内 sp² C-C σ 键(~610 kJ/mol)+ 离域 π 键→极高面内强度+导电性；层间 van der Waals→弱结合→可滑移/可剥离。每个 C 贡献 1 个 pz 电子形成 π 共轭体系→π→π* 带间跃迁→Dirac 锥电子结构(理想石墨烯)/窄能隙半导体(缺陷石墨烯)",
            "type": "first_principles_insight"
        },
        "structure_to_properties": {
            "property": "第一性原理 · 结构→性质推导",
            "value": "【导电性(PAPER-006: 电阻率从 26.8→2.9×10⁷ Ω·m)】sp² π 电子离域→层内载流子迁移率高→电子隧道效应→导电网络。【导热性(PAPER-006: 导热↑6.9倍)】sp² 键→高德拜温度→高声子速度→面内高导热(弹道输运)。【润滑性】层间弱 van der Waals→层间易滑移→固体润滑剂。【C-O 缺陷→反应活性】缺陷位 sp³ 碳→悬挂键→可功能化接枝/吸附位点",
            "type": "first_principles_insight"
        },
        "derived_possibilities": {
            "property": "第一性原理 · 推导可能新性质",
            "value": "① 类石墨烯碳层→电化学储能(超级电容器/锂电负极)→sp² 碳+缺陷位→高比电容/嵌锂容量。② 碳层包覆陶瓷颗粒→核-壳结构→阻隔热腐蚀+导电双功能。③ 层间插层化学→可插入离子/分子→改性碳层电子结构(类似石墨插层化合物 GIC)。④ sp² 碳+缺陷→氧还原反应(ORR)催化活性位→潜在无金属电催化剂。⑤ 碳层表面等离子体效应→SERS 基底候选(增强拉曼信号)",
            "type": "first_principles_insight"
        }
    },

    # ===== dehydrated_talc: 脱水滑石 =====
    "dehydrated_talc": {
        "structure_summary": {
            "property": "第一性原理 · 晶体结构",
            "value": "与滑石原矿相同(2:1 TOT 层状硅酸盐, P1 三斜)，仅表面物理吸附水脱除，TOT 层结构完整, d(006) 未变化。层间碳层保留",
            "type": "first_principles_insight"
        },
        "bond_analysis": {
            "property": "第一性原理 · 化学键 + 脱水机理",
            "value": "吸附水以氢键结合于 TOT 层外表面(非层间)→结合能弱(<40 kJ/mol vs 层间 OH ~400 kJ/mol)→30-165°C 即可脱除。质量损失仅 0.32%，不含结构 OH 断裂→Si-O/Mg-O 键全保留→晶体结构不变",
            "type": "first_principles_insight"
        },
        "structure_to_properties": {
            "property": "第一性原理 · 结构→性质推导",
            "value": "脱除吸附水后表面暴露 Si-O-Si/Si-OH/Mg-OH 位点→表面能增加→轻微疏水性改变→后续加热过程中反应活性微增。但整体性质(硬度/层间距/结构稳定性)与原矿几乎相同",
            "type": "first_principles_insight"
        },
        "derived_possibilities": {
            "property": "第一性原理 · 推导可能新性质",
            "value": "脱水后表面活性位暴露→可作为温和预处理步骤→增强后续表面功能化(硅烷接枝、离子交换)效率。脱水温度低(165°C)→能耗极低→工业友好预处理",
            "type": "first_principles_insight"
        }
    },

    # ===== decarbonized_talc: 脱碳滑石 =====
    "decarbonized_talc": {
        "structure_summary": {
            "property": "第一性原理 · 晶体结构",
            "value": "TOT 层状结构保留但层间距微胀(d(006): 0.313→0.315 nm)。层间有机碳氧化为 CO₂ 逸出→层间留下纳米空隙→层间距轻微膨胀。TOT 层内 Si-O/Mg-O 键仍完整",
            "type": "first_principles_insight"
        },
        "bond_analysis": {
            "property": "第一性原理 · 化学键 + 脱碳机理",
            "value": "层间有机碳 sp²/sp³ C-C/C-H 键 + O₂ → CO₂↑ + H₂O↑ (氧化燃烧反应, 165-580°C)。CO₂ 分子(~0.33 nm 动力学直径)从层间逸出时撑开 TOT 层→d(006) 膨胀。有机碳完全氧化后层间仅余 van der Waals 间隙→白度开始提升(DSC 336.7°C 吸热谷验证)",
            "type": "first_principles_insight"
        },
        "structure_to_properties": {
            "property": "第一性原理 · 结构→性质推导",
            "value": "脱碳后: ① 白度提升→有机碳(致黑)→去除→视觉白度↑。② 层间空隙→微增 BET 比表面→反应活性微增。③ 层间距微胀→TOT 层间结合力略有减弱→后续脱羟基温度略降低。④ CO₂ 逸出通道可能成为后续反应(酸浸/插层)的传质通道",
            "type": "first_principles_insight"
        },
        "derived_possibilities": {
            "property": "第一性原理 · 推导可能新性质",
            "value": "① 层间纳米空隙→可作为分子筛分通道→选择性吸附小分子(H₂O/CO₂)。② 脱碳后层间干净→利于后续插层化学(客体分子/离子无障碍进入层间)。③ 有机碳氧化为 CO₂ 可利用→若在封闭系统中可捕获 CO₂→碳负排放工艺设计",
            "type": "first_principles_insight"
        }
    },

    # ===== dehydroxylated_talc: 脱羟基滑石 =====
    "dehydroxylated_talc": {
        "structure_summary": {
            "property": "第一性原理 · 晶体结构",
            "value": "部分非晶化：TOT 层状结构残留但长程有序丧失。OH 从八面体层脱除→Mg(O,OH)₆ 八面体→MgO₅ 畸变多面体+部分 MgO₆ 八面体。Si-O 四面体网络部分保留→无定形 SiO₂/MgO 纳米域形成。结晶度 CI 从 75.8% 降至 51.0%(T800→T900, PAPER-005)",
            "type": "first_principles_insight"
        },
        "bond_analysis": {
            "property": "第一性原理 · 化学键 + 脱羟基机理",
            "value": "Mg-OH 键断裂(键能 ~380-400 kJ/mol, >800°C)→2(OH⁻)→O²⁻+H₂O↑(脱羟基反应)。OH 脱除后八面体层 Mg-O 配位失衡→Mg 配位数从 6 向 5/4 过渡→Mg-O 多面体重排→无定形 MgOₓ 域形成。Si-O-Si 桥键在 800-900°C 可维持→SiO₄ 四面体框架尚有残留(PAPER-005: 1017→1000 cm⁻¹ 红移表明 Si-O-Si 角变化但键未断)",
            "type": "first_principles_insight"
        },
        "structure_to_properties": {
            "property": "第一性原理 · 结构→性质推导",
            "value": "【活化窗口 800-900°C(PAPER-005)】OH 脱除+部分非晶化→表面丰富断键/悬挂键→高反应活性→酸浸效率大幅提高(对比未煅烧滑石几乎不酸溶)。【Zeta 电位降至一半】OH 脱除→表面质子化/去质子化位减少→表面电荷密度降→胶体稳定性改变。【FTIR 红移(3676→3666, 1017→1000 cm⁻¹)】OH 脱除→残余 OH 环境变化+Si-O 键角变形→力常数降低→振动频率红移",
            "type": "first_principles_insight"
        },
        "derived_possibilities": {
            "property": "第一性原理 · 推导可能新性质",
            "value": "① 非晶化+高比表面→天然'活性中间体'→作为前驱体合成其他 Mg-Si 基材料(无需完全分解为顽火辉石)。② 表面断键→高化学吸附活性→CO₂ 捕获剂(MgO 碳化)+重金属离子吸附剂。③ 无定形 MgO-SiO₂ 混合域→类地质聚合物前驱体→碱激发胶凝材料(类似矿渣/粉煤灰)。④ 介孔保留(4.0 nm)+表面活化→双功能(吸附+催化)→催化剂载体或吸附剂",
            "type": "first_principles_insight"
        }
    },

    # ===== acid_activated_enstatite: 酸活化顽火辉石 =====
    "acid_activated_enstatite": {
        "structure_summary": {
            "property": "第一性原理 · 晶体结构",
            "value": "顽火辉石(Pbca)经 HCl 酸活化→Mg²⁺ 从 MgO₆ 八面体位部分溶出→H⁺(以 H₃O⁺ 形式, r≈0.135 nm)取代 Mg²⁺(r=0.072 nm)→c 轴膨胀(0.51052→0.52587 nm, PAPER-003)。Si-O 四面体链骨架保留→酸活化是'选择性溶解'而非整体溶解",
            "type": "first_principles_insight"
        },
        "bond_analysis": {
            "property": "第一性原理 · 化学键 + 酸溶选择性机理",
            "value": "选择性溶解由键型差异决定：Mg-O 离子键(键能 ~167 kJ/mol)→H⁺ 攻击→Mg²⁺ + 2H₂O → [Mg(H₂O)₆]²⁺(水合)→溶出。Si-O 共价键(键能 ~466 kJ/mol)→H⁺ 攻击无效→Si-O-Si 桥键不被 HCl 断裂→SiO₄ 链保留。H₃O⁺ 半径(0.135 nm)远大于 Mg²⁺(0.072 nm)→进入八面体空穴后撑大晶格→c 轴膨胀。石英(SiO₂)共存相→完全耐酸→结构保留",
            "type": "first_principles_insight"
        },
        "structure_to_properties": {
            "property": "第一性原理 · 结构→性质推导",
            "value": "【Mg²⁺ 溶出 352 mmol/L (16h, PAPER-003)】Mg-O 键弱→H⁺ 攻击效率高→大量 Mg²⁺ 溶出。【结晶度下降(FWHM: 0.214→0.280)】H₃O⁺ 取代→晶格膨胀+无序增加→XRD 峰宽化。【BET 增加(定性)】Mg 溶出→八面体位留空→微孔/介孔增加→比表面积增大。【硅骨架保留→可进一步功能化】Si-O 链残存→可作为模板/载体→后续离子重建(PAPER-003 Zn²⁺ 晶格重建)",
            "type": "first_principles_insight"
        },
        "derived_possibilities": {
            "property": "第一性原理 · 推导可能新性质",
            "value": "① 溶出 Mg²⁺后留下的 SiO₄ 骨架→天然介孔/微孔材料→分子筛前驱体或吸附剂。② H⁺ 交换位→可进一步离子交换植入其他功能阳离子(Ag⁺/Cu²⁺/稀土等)→多品种功能材料平台(不仅抗菌)。③ Mg²⁺ 溶出液→可沉淀为 Mg(OH)₂/MgO 纳米颗粒→高纯镁产品线(已验证 PAPER-007)。④ 酸活化作为通用'激活'步骤→任何需要暴露 Si-O 表面或增加反应活性的下游工艺均可用",
            "type": "first_principles_insight"
        }
    }
}


def add_first_principles(tree: dict, dry_run: bool = False) -> dict:
    """为所有 intermediate_phase + raw_material 节点注入第一性原理分析。"""
    nodes = tree.get("nodes", {})
    stats = {"updated": [], "skipped": [], "props_added": 0}

    for nid, node in nodes.items():
        node_type = node.get("type", "")
        if node_type not in ("raw_material", "intermediate_phase"):
            stats["skipped"].append(f"{nid} (type={node_type})")
            continue

        if nid not in FIRST_PRINCIPLES_DATA:
            stats["skipped"].append(f"{nid} (无第一性原理数据)")
            continue

        fp_data = FIRST_PRINCIPLES_DATA[nid]
        existing_props = node.setdefault("properties", [])

        # 检查是否已存在第一性原理数据（避免重复注入）
        existing_types = {p.get("type") for p in existing_props}
        if "first_principles_insight" in existing_types:
            stats["skipped"].append(f"{nid} (已有第一性原理数据)")
            continue

        added_count = 0
        for fp_prop in fp_data.values():
            existing_props.append(deepcopy(fp_prop))
            added_count += 1

        stats["updated"].append(f"{nid} (+{added_count} 第一性原理性质)")
        stats["props_added"] += added_count

    return stats


def main():
    dry_run = "--dry-run" in sys.argv

    with open(TREE_PATH, "r", encoding="utf-8") as f:
        tree = json.load(f)

    stats = add_first_principles(tree, dry_run=dry_run)

    print("=" * 60)
    print("第一性原理数据注入报告")
    print("=" * 60)
    print(f"\n✅ 已更新节点 ({len(stats['updated'])} 个):")
    for s in stats["updated"]:
        print(f"   {s}")
    print(f"\n⏭️  跳过节点 ({len(stats['skipped'])} 个):")
    for s in stats["skipped"]:
        print(f"   {s}")
    print(f"\n📊 总计新增第一性原理性质: {stats['props_added']} 条")

    if dry_run:
        print("\n[DRY-RUN] 未写入磁盘。")
    else:
        with open(TREE_PATH, "w", encoding="utf-8") as f:
            json.dump(tree, f, ensure_ascii=False, indent=2)
        print(f"\n[OK] 已写入 {TREE_PATH}")
        print(f"  版本: {tree['meta']['version']} | 节点: {len(tree['nodes'])} | 边: {len(tree['edges'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
