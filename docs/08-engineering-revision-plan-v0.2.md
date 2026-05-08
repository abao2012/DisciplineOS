# DisciplineOS Engineering Revision Plan v0.2

鏈枃妗ｄ緷鎹?`DisciplineOS_Engineering_Spec_v0.2.docx` 鍒跺畾锛岀敤浜庢妸褰撳墠鍙繍琛屽師鍨嬫帹杩涘埌宸ョ▼鍖栫郴缁熴€傚師鍒欐槸澧為噺鏀归€狅紝涓嶆帹鍊掗噸鏉ワ紱Web UI 缁х画浣滀负涓诲叆鍙ｏ紝CLI 淇濈暀涓鸿嚜鍔ㄥ寲鍜屾祴璇曞叆鍙ｃ€?
## 1. 淇鐩爣

v0.2 鐨勭洰鏍囦笉鏄鍔犱竴涓紨绀洪〉闈紝鑰屾槸琛ラ綈闀挎湡鍙敤绯荤粺鐨勫伐绋嬪湴鍩猴細

- SQLite 浣滀负榛樿涓诲瓨鍌紝PostgreSQL 淇濈暀涓洪珮绾ч€夐」锛孞SON 浣滀负 legacy/export銆?- 鏂板 Settings锛屾寔涔呭寲 `storage_mode`銆乣ai_enabled`銆乣strict_mode`銆?- 鏂板 Data Source Center锛岄厤缃?Manual/CSV/Excel/QMT/TuShare/AkShare 绛?Provider銆?- 鏂板 Capability Mapping锛岃 positions銆乼rades銆乸rice銆乿olume銆乫inancial 绛夎兘鍔涘彲鐙珛鏄犲皠涓绘簮鍜屽鐢ㄦ簮銆?- Discipline Card Generator 鍗囩骇涓?Card Wizard锛岀敤鎴烽€夋嫨鍜岃嚜瀹氫箟鍐呭蹇呴』娌夋穩涓虹粨鏋勫寲 `card_rules`銆?- Decision Gate 缁х画鐢?Rule Engine 杈撳嚭鏈€缁堢姸鎬侊紝AI 鍜屾暟鎹簮鍙彁渚?evidence銆乪xplanation銆乺eview draft锛屼笉鏀瑰彉鏈€缁堣鍐炽€?
## 2. 褰撳墠瀹炵幇宸窛

| 妯″潡 | 褰撳墠鐘舵€?| v0.2 宸窛 |
| --- | --- | --- |
| Web UI | 宸插彲杩愯锛屽惈鍗＄墖銆佸鏌ャ€佸鍏ャ€佸鐩?| 缂?Settings銆丏ata Source Center銆丆ard Wizard 閫夐」寮忚鍒欑粦瀹?|
| 瀛樺偍 | JSON 鏂囦欢涓轰富 | 闇€瑕?SQLite 榛樿涓诲瓨鍌ㄥ拰杩佺Щ鍏煎 |
| 鏁版嵁婧?| CSV/Excel 瀵煎叆鍏ュ彛 | 缂?Provider 閰嶇疆銆佽繛鎺ユ祴璇曘€佽兘鍔涙槧灏勩€佸悓姝ョ姸鎬?|
| 绾緥鍗?| 鍙敓鎴愭枃鏈邯寰嬪崱 | 缂虹粨鏋勫寲 `card_rules` 鍜岄€夐」寮忓悜瀵?|
| Decision Gate | 鏈変粨浣嶃€佽瘉鎹€佹儏缁€佽储鎶ャ€侀€昏緫婕傜Щ瑙勫垯 | 闇€寮曠敤 Evidence Engine 鍜?card_rules 鍙傛暟 |
| Monthly Review | 宸蹭粠鍘嗗彶瀹℃煡鑱氬悎 | 鍚庣画闇€鍏ㄩ儴鍩轰簬鏁版嵁搴撳巻鍙蹭笌 evidence |
| AI/Copilot | 鏈湴妯℃澘鍖栬緭鍑?| 闇€ Settings 寮€鍏炽€佸悎瑙勮繃婊ゃ€佽皟鐢ㄥ璁?|

## 3. 鍒嗛樁娈佃鍒?
### v0.2.1 鏁版嵁搴撲笌璁剧疆

- 鏂板 SQLite schema锛歚system_settings`銆乣data_sources`銆乣data_capabilities`銆乣data_sync_logs`銆?- 鏂板 Repository 灞傦紝鏈嶅姟灞備笉鐩存帴鎿嶄綔鏁版嵁搴撶粏鑺傘€?- 淇濈暀 JSON legacy/export锛岀幇鏈?demo 鍜屾祴璇曚笉鍥為€€銆?- Web UI 澧炲姞 Settings 闈㈡澘銆?
楠屾敹锛氬惎鍔ㄥ悗鑷姩鍒涘缓 `disciplineos.db`锛涜缃埛鏂板悗浠嶄繚鐣欙紱鍘熸湁 demo銆亀eb銆乸ytest 缁х画閫氳繃銆?
### v0.2.2 Data Source Center

- UI 鏀寔 Provider 淇濆瓨銆佸惎鐢?绂佺敤銆佷紭鍏堢骇銆佹湰鍦拌矾寰?API Base銆?- 鍚庣鏀寔 Manual/CSV/Excel 鏈湴璺緞娴嬭瘯锛孮MT/TuShare/AkShare 鍏堜繚瀛橀厤缃苟鏄剧ず寰呮帴鍏ョ姸鎬併€?- UI 鏀寔 positions銆乼rades銆乸rice_daily銆乿olume銆乫inancial_metrics 鐨勮兘鍔涙槧灏勩€?
楠屾敹锛氬彲淇濆瓨 Provider锛涘彲淇濆瓨鑳藉姏鏄犲皠锛汥ashboard 鍙洖鏄鹃厤缃拰娴嬭瘯缁撴灉銆?
### v0.2.3 Discipline Card Wizard

- 鍏棶寮忓悜瀵煎姞鍏ユā鏉块€夐」鍜岃嚜瀹氫箟杈撳叆銆?- 淇濆瓨鍗＄墖鏃剁敓鎴?`card_rules`銆?- 棣栨壒缁撴瀯鍖栬鍒欙細`position.max_single`銆乣evidence.required_for_add`銆乣earnings.no_unplanned_add`銆乣thesis.review_required`銆?
楠屾敹锛氱敓鎴愮邯寰嬪崱鍚庡彲鍦ㄦ暟鎹腑鐪嬪埌 `card_rules`锛涙瘡鏉℃柊澧炶鍒欐湁娴嬭瘯銆?
### v0.2.4 Evidence Engine 涓?Decision Gate 寮哄寲

- 鏂板 `evidence_items` 姒傚康锛屾妸璐㈡姤鎽樿銆佺敤鎴疯緭鍏ャ€佽鎯?閲忚兘/鍏憡璇佹嵁缁熶竴鍏ユ睜銆?- Decision Gate 寮曠敤 evidence_items锛岃€屼笉鏄彧鐪嬬敤鎴锋墜鍔ㄨ緭鍏ユ枃瀛椼€?- 寮哄寲瑙勫垯鐘舵€侊細`BLOCKED`銆乣EVIDENCE_REQUIRED`銆乣REVIEW_REQUIRED`銆?
楠屾敹锛氭棤鏂板璇佹嵁鍔犱粨瑙﹀彂 evidence required锛涗粨浣嶈秴闄愩€佹儏缁姞浠撱€佽储鎶ュ墠鏃犻妗堢户缁‖闃绘柇銆?
鎵ц鐘舵€侊細宸插畬鎴愭渶灏忓伐绋嬮棴鐜€傚綋鍓嶇増鏈凡鏂板 `EvidenceItem` 妯″瀷銆丼QLite `evidence_items` 琛ㄣ€丷epository/Service/Web API/UI 鍏ュ彛锛涜储鎶ユ憳瑕佷細鑷姩娌夋穩涓?`financial_result` evidence锛汥ecision Gate 鍦ㄧ敤鎴锋湭鎵嬪姩濉啓 evidence 鏃讹紝浼氳嚜鍔ㄥ紩鐢ㄥ悓鏍囩殑鏈€杩?evidence_items銆?
### v0.2.5 AI 鍙€夊眰涓庡璁?
- Settings 鎺у埗 AI 寮€鍏炽€?- AI 杈撳嚭鍙厑璁?evidence銆乪xplanation銆乺eview draft銆乺ule revision suggestion銆?- 澧炲姞 `ai_runs` 瀹¤璁板綍鍜屽悎瑙勮繃婊ゃ€?
楠屾敹锛氬叧闂?AI 鏃剁郴缁熷畬鍏ㄥ彲鐢紱寮€鍚?AI 涓嶈緭鍑轰拱鍗栧缓璁€佺洰鏍囦环鎴栨敹鐩婇娴嬶紱鏈€缁堢姸鎬佷粛鐢?Rule Engine 鍐冲畾銆?
鎵ц鐘舵€侊細宸插畬鎴愭渶灏忓伐绋嬮棴鐜€傚綋鍓嶇増鏈柊澧?`ai_guardrails.py`銆乣ai_runs` SQLite 琛ㄣ€丷epository/Service/Web API 瀹¤鍏ュ彛锛汣opilot 杈撳嚭浼氱粡杩囧悎瑙勮繃婊わ紝AI 寮€鍚椂鍐欏叆 `ai_runs`锛孉I 鍏抽棴鏃朵繚鎸佹湰鍦扮‘瀹氭€ц緭鍑轰笖涓嶄骇鐢?AI 瀹¤璁板綍銆侱ashboard 鏄庣‘鏄剧ず `final_status_source = rule_engine`銆?
## 4. 鏈疆宸叉墽琛?
- 鏂板 SQLite 榛樿瀛樺偍涓?schema 鍒濆鍖栥€?- 鏂板 `repositories.py`锛屽皝瑁呮枃妗ｈ鍐欍€丼ettings銆丏ata Source銆丆apability Mapping銆?- 鏈嶅姟灞傛帴鍏?Repository锛孌ashboard 杩斿洖 settings/data_sources/data_capabilities銆?- Web API 鏂板 `/api/settings`銆乣/api/data-sources`銆乣/api/data-capabilities`銆?- Web UI 鏂板 Settings 鍜?Data Source Center 闈㈡澘銆?- Discipline Card 澧炲姞 `card_rules` 瀛楁锛岀敓鎴愬櫒浼氭牴鎹叚闂瓟妗堢敓鎴愰鎵圭粨鏋勫寲瑙勫垯銆?- 鏂板 Repository/Settings/DataSource 娴嬭瘯銆?- 鏂板 Evidence Engine锛氭墜鍔ㄨ瘉鎹€佽储鎶ヨ瘉鎹叆姹犮€丏ashboard 鍥炴樉銆丏ecision Gate 鑷姩寮曠敤璇佹嵁姹犮€?- 鏂板 AI 鍙€夊眰鎶ゆ爮锛歋ettings 寮€鍏炽€佸悎瑙勮繃婊ゃ€乣ai_runs` 瀹¤銆丆opilot 鏈€缁堣鍐虫潵婧愭爣璁般€?
## 5. 涓嬩竴姝?
### v0.2.6 Rule Engine 鍙傛暟鍖栦笌鐘舵€佺粏鍖?
- `card_rules` 绾冲叆 Rule Engine 鎵ц锛屼笉鍐嶅彧鏄崱鐗囦笂鐨勭粨鏋勫寲闄勫睘鏁版嵁銆?- `position.max_single` 鏀寔璇诲彇 `card_rules.params.max_position_pct`銆?- `evidence.required_for_add` 鏀寔浣滀负鐙珛瑙勫垯瑙﹀彂銆?- `EVIDENCE_REQUIRED` 鍜?`REVIEW_REQUIRED` 鎴愪负姝ｅ紡 `AuditStatus`銆?- 鐘舵€佷紭鍏堢骇锛歚BLOCKED` > `EVIDENCE_REQUIRED` > `REVIEW_REQUIRED` > `WARN` > `PASS`銆?
楠屾敹锛氫粨浣嶈秴闄愪粛鐒剁‖闃绘柇锛涚己璇佹嵁涓嶅啀鍙槸鏅€?warning锛涢€昏緫婕傜Щ鎴栭噸澶ф搷浣滃悗澶嶇洏瑕佹眰鍙互琚?UI 鍜屽璁＄嫭绔嬭瘑鍒€?
鎵ц鐘舵€侊細宸插畬鎴愩€傛柊澧炶鍒欏紩鎿庢祴璇曡鐩?card_rules 鍙傛暟鍖栦粨浣嶃€佽瘉鎹繀闇€鐘舵€併€佸鐩樺繀闇€鐘舵€侊紱鏈嶅姟灞傛祴璇曞凡鍚屾鏇存柊銆?
## 6. 涓嬩竴姝?
涓嬩竴杞簲杩涘叆 v0.2.7锛氭妸 Rule Engine 鐨勯€愭潯缁撴灉鎸佷箙鍖栦负 `rule_results`锛岃 UI 鑳藉睍寮€鏌ョ湅姣忔潯瑙勫垯鐨勭姸鎬併€佹潵婧愩€佸弬鏁板拰鍛戒腑鍘熷洜锛岃€屼笉鏄彧鐪嬪埌鏈€缁?status 涓?violations/warnings銆?
### v0.2.7 Rule Results 瀹¤鏄庣粏

- 鏂板 SQLite `rule_results` 琛ㄣ€?- 姣忔 Decision Gate 瀹℃煡鍚庯紝淇濆瓨鎵€鏈夎鍒欑殑鎵ц缁撴灉锛屽寘鎷?PASS 瑙勫垯銆?- 姣忔潯缁撴灉璁板綍 `decision_id`銆乣rule_code`銆乣rule_name`銆乣status`銆乣severity`銆乣category`銆乣message`銆乣params`銆?- `/api/check` 杩斿洖鏈 `rule_results`銆?- `/api/rule-results` 鏀寔鏌ヨ瑙勫垯缁撴灉銆?- Dashboard 杩斿洖鏈€杩戣鍒欑粨鏋滐紝UI 鍙湪鍗虫椂瀹℃煡缁撴灉鍜屽巻鍙插鏌ヤ腑灞曞紑鏌ョ湅銆?
楠屾敹锛氱敤鎴疯兘鐪嬪埌鏈€缁堢粨璁鸿儗鍚庣殑姣忔潯瑙勫垯鎵ц鏄庣粏锛涘弬鏁板寲瑙勫垯鑳芥樉绀虹敓鏁堝弬鏁帮紱娌℃湁鍛戒腑鐨勮鍒欎篃鑳芥樉绀?PASS锛屽舰鎴愬畬鏁村璁￠摼璺€?
鎵ц鐘舵€侊細宸插畬鎴愩€傛柊澧炶鍒欑粨鏋滅敓鎴愩€丼QLite/JSON 鎸佷箙鍖栥€乄eb API銆乁I 灞曞紑瑙嗗浘鍜屾祴璇曡鐩栥€?
## 7. 涓嬩竴姝?
涓嬩竴杞簲杩涘叆 v0.2.8锛氬己鍖?Discipline Card Wizard 鐨勯€夐」寮?UI锛屾妸鏂囨。涓殑鍏棶榛樿閫夐」鐩存帴鍋氭垚鍙偣閫夈€佸閫夈€佸彲鑷畾涔夌殑鎺т欢锛岃€屼笉鍙槸 textarea銆?
### v0.2.8 Discipline Card Wizard 閫夐」寮?UI

- Card templates 澧炲姞 `thesis_options`銆?- Web UI 涓叚闂敼涓衡€滄ā鏉块€夐」澶氶€?+ 鑷畾涔夎緭鍏モ€濄€?- 浠撲綅闂澧炲姞 5%/10%/15%/20%/25%/30% 鍙婃ā鏉块粯璁ゅ€兼寜閽€?- 鎻愪氦鏃跺悎骞跺凡閫夐€夐」鍜岃嚜瀹氫箟 textarea锛屽苟鍘婚噸銆?- 妯℃澘鍒囨崲鏃惰嚜鍔ㄥ埛鏂板叚闂粯璁ら€夐」銆?
楠屾敹锛氱敤鎴蜂笉闇€瑕佷粠绌虹櫧 textarea 寮€濮嬪啓绾緥鍗★紱鍙互鐩存帴鐐归€夋ā鏉跨邯寰嬶紝涔熷彲浠ヨˉ鍏呰嚜宸辩殑瑙勫垯锛涗繚瀛樺悗浠嶇敓鎴?discipline card 涓?`card_rules`銆?
鎵ц鐘舵€侊細宸插畬鎴愩€傛柊澧炴ā鏉块€夐」銆佸墠绔悜瀵兼覆鏌撱€佷粨浣嶆寜閽€佸閫夊悎骞舵彁浜ゃ€佹牱寮忓拰娴嬭瘯瑕嗙洊銆?
## 8. 涓嬩竴姝?
涓嬩竴杞簲杩涘叆 v0.2.9锛氬寮?Data Source Center 鐨勫鍏ュ伐浣滄祦锛屾妸 Provider/Capability Mapping 涓?CSV/Excel import 鍏宠仈璧锋潵锛屽舰鎴愨€滄寜鑳藉姏浠庨厤缃簮瀵煎叆鈥濈殑璺緞锛岃€屼笉鏄彧鏈夌嫭绔嬫枃浠跺鍏ヨ〃鍗曘€?
### v0.2.9 Data Source Center 鍚屾宸ヤ綔娴?
- Provider 閰嶇疆涓殑 `config.local_path` 鍙綔涓?CSV/Excel 鏁版嵁婧愯矾寰勩€?- Capability Mapping 涓庡鍏ヨ兘鍔涘叧鑱旓紝褰撳墠鏀寔 `positions`銆乣trades`銆?- 鏂板 `/api/data-sync`锛屾寜 capability 鏌ユ壘鍚敤鐨勬渶浣庝紭鍏堢骇 Provider 骞惰Е鍙戝鍏ャ€?- 姣忔鍚屾鍐欏叆 `data_sync_logs`锛岃褰?provider銆乻ync_type銆乻tatus銆乵essage銆乻tarted_at銆乫inished_at銆?- Dashboard 鍜?Data Source Center UI 鏄剧ず鏈€杩戝悓姝ユ棩蹇椼€?
楠屾敹锛氱敤鎴峰彲浠ュ厛淇濆瓨 Provider锛屽啀淇濆瓨 capability mapping锛岀劧鍚庣偣鍑?Sync From Mapped Provider 瀵煎叆鎸佷粨鎴栦氦鏄撴祦姘达紱鍚屾缁撴灉鍙拷韪€?
鎵ц鐘舵€侊細宸插畬鎴愩€傛柊澧炴湇鍔″眰鍚屾閫昏緫銆乄eb API銆乁I 琛ㄥ崟銆佸悓姝ユ棩蹇楀睍绀哄拰娴嬭瘯瑕嗙洊銆?
## 9. 涓嬩竴姝?
涓嬩竴杞簲杩涘叆 v0.2.10锛氭妸 Data Source Center 鐨?Provider 娴嬭瘯鑳藉姏鍋氱粏锛屽尯鍒?Manual/CSV/Excel/QMT/TuShare/AkShare 鐨?connector status锛屽苟缁欐湭鎺ュ叆鐨?Provider 鏄庣‘鏄剧ず鈥滈厤缃凡淇濆瓨 / connector 鏈疄鐜?/ 闇€瑕?token 鎴栨湰鍦颁緷璧栤€濄€?
### v0.2.10 Provider Connector Status

- Manual provider 杩斿洖鍙敤鐘舵€併€?- CSV/Excel provider 妫€鏌?`config.local_path` 鏄惁瀛樺湪锛屽苟鏍￠獙鏂囦欢鍚庣紑銆?- QMT provider 妫€鏌ユ湰鍦拌矾寰勶紱璺緞鍙揪浣?connector 鏈疄鐜版椂杩斿洖 `not_implemented`銆?- TuShare provider 妫€鏌?`api_token`锛泃oken 瀛樺湪浣?connector 鏈疄鐜版椂杩斿洖 `not_implemented`銆?- AkShare provider 妫€鏌?Python 渚濊禆锛涗緷璧栫己澶辨椂杩斿洖 `blocked`銆?- Eastmoney / Yahoo Finance / Custom API 杩斿洖鏄庣‘鐨勬湭瀹炵幇鎴栫己閰嶇疆鐘舵€併€?- Data Source Center UI 澧炲姞 API Token 鍜?API Base URL 瀛楁銆?
楠屾敹锛氱敤鎴蜂繚瀛?Provider 鍚庤兘鐪嬪埌鏄庣‘鐘舵€侊紝涓嶉渶瑕佺寽娴嬫槸璺緞閿欍€乼oken 缂哄け銆佷緷璧栫己澶憋紝杩樻槸 connector 灏氭湭寮€鍙戙€?
鎵ц鐘舵€侊細宸插畬鎴愩€傛柊澧?provider 鐘舵€佺粏鍖栭€昏緫銆乁I 閰嶇疆瀛楁鍜屾祴璇曡鐩栥€?
## 10. 涓嬩竴姝?
涓嬩竴杞簲杩涘叆 v0.2.11锛氬皢 Financial Evidence 涓?Evidence Engine 鏇存繁鏁村悎锛屽鍔?evidence type 杩囨护銆佹寜 symbol 鏌ヨ銆佷互鍙?Decision Gate 涓€滄湰娆″紩鐢ㄤ簡鍝簺 evidence_items鈥濈殑鍙鍖栥€?
### v0.2.11 Evidence Query 涓庡紩鐢ㄥ彲瑙嗗寲

- `/api/evidence` 鏀寔 `symbol` 鍜?`evidence_type` 鏌ヨ鍙傛暟銆?- Evidence Engine UI 澧炲姞 symbol/type 杩囨护琛ㄥ崟銆?- Decision Gate 鑷姩寮曠敤璇佹嵁姹犳椂锛屼細鍦ㄧ粨鏋滀腑杩斿洖 `referenced_evidence_items`銆?- 鍐崇瓥鍘嗗彶涓細淇濆瓨 `referenced_evidence_ids`銆?- 鍗虫椂瀹℃煡缁撴灉鏄剧ず Referenced Evidence锛岀敤鎴疯兘鐪嬪埌鏈瀹℃煡瀹為檯鐢ㄤ簡鍝簺璇佹嵁銆?
楠屾敹锛氱敤鎴峰彲浠ユ寜鏍囩殑鍜岃瘉鎹被鍨嬭繃婊よ瘉鎹睜锛涗氦鏄撳墠瀹℃煡涓嶅啀鍙槸鎶婅瘉鎹枃鏈杩?reason锛岃€屾槸鏄庣‘鏄剧ず琚紩鐢ㄧ殑 evidence_items銆?
鎵ц鐘舵€侊細宸插畬鎴愩€傛柊澧炲悗绔繃婊ゃ€佸鏌ュ紩鐢ㄨ繑鍥炪€乁I 灞曠ず鍜屾祴璇曡鐩栥€?
## 11. 涓嬩竴姝?
涓嬩竴杞簲杩涘叆 v0.2.12锛氬皢 Evidence Engine 鐨勫紩鐢ㄤ粠鈥滆嚜鍔ㄥ彇鏈€杩?5 鏉♀€濆崌绾т负鍙€夋嫨寮曠敤锛屽湪 Decision Gate UI 涓寜 symbol 灞曠ず鍊欓€?evidence_items锛岃鐢ㄦ埛鍕鹃€夋湰娆″鏌ヨ寮曠敤鐨勮瘉鎹€?
### v0.2.12 Selectable Evidence References

- Decision Gate payload 鏀寔 `evidence_item_ids`銆?- 鍚庣鍙寜 id 绮剧‘璇诲彇 evidence_items锛屽苟鍙紩鐢ㄧ敤鎴峰嬀閫夌殑璇佹嵁銆?- 鑻ョ敤鎴锋湭鍕鹃€変笖鏈墜濉?evidence锛岀郴缁熶粛鑷姩寮曠敤鍚屾爣鐨勬渶杩?evidence_items 浣滀负鍏滃簳銆?- Decision Gate UI 鎸夊綋鍓?symbol 灞曠ず鍊欓€?evidence_items銆?- 瀹℃煡鎻愪氦鏃舵妸鍕鹃€夌殑 evidence ids 涓€骞舵彁浜ゃ€?
楠屾敹锛氱敤鎴疯兘鏄庣‘鎺у埗鏈瀹℃煡寮曠敤鍝簺璇佹嵁锛涘鏌ョ粨鏋滃拰 decision 璁板綍鍙拷婧埌鍏蜂綋 evidence ids銆?
鎵ц鐘舵€侊細宸插畬鎴愩€傛柊澧炴樉寮?evidence id 寮曠敤銆乁I 璇佹嵁鍕鹃€夈€佽嚜鍔ㄥ厹搴曞拰娴嬭瘯瑕嗙洊銆?
## 12. 涓嬩竴姝?
涓嬩竴杞簲杩涘叆 v0.2.13锛氬皢 Monthly Review 杩涗竴姝ユ暟鎹簱鍖栵紝鎶?`reviews` 琛ㄨ惤鍦帮紝骞舵敮鎸佸皢鏌愪釜鏈堢殑澶嶇洏蹇収淇濆瓨涓嬫潵锛岄伩鍏嶆瘡娆″彧涓存椂璁＄畻銆?

### v0.2.13 Monthly Review Snapshots

- Add SQLite `reviews` table for persisted monthly review snapshots.
- Save the computed monthly review as an immutable snapshot with `period`, `review_json`, `discipline_score`, `decision_count`, `status_summary`, and `created_at`.
- Add service/repository APIs for saving and listing review snapshots.
- Add `/api/reviews` GET/POST endpoints.
- Add UI action in Monthly Review to save the current month snapshot and list saved snapshots.
- Keep JSON legacy/export compatibility through `reviews.json`.

Acceptance: the user can select a month, save the current review as a snapshot, refresh the page, and still see the saved review history for that period.

Status: completed. SQLite persistence, legacy export, Web API, UI controls, and regression test coverage are implemented.

## 13. Next Step

Next v0.2.14 should add review drill-down from a saved snapshot: show the exact decisions, rule results, violations, and evidence references that produced the snapshot, so monthly review can become an auditable report rather than only a score summary.

### v0.2.14 Review Snapshot Drill-down

- Add a persisted `drilldown` section to each newly saved monthly review snapshot.
- Freeze the exact monthly decisions, audits, rule results, violations, and referenced evidence items inside the snapshot payload.
- Render saved snapshots as expandable audit reports in the Monthly Review UI.
- Preserve backwards compatibility for older snapshots that do not yet contain drill-down data.
- Add regression coverage for snapshots with referenced evidence.

Acceptance: after saving a monthly review snapshot, the user can expand it and inspect the concrete decisions, rule checks, violations, and evidence records that produced the saved score.

Status: completed. Snapshot drill-down is generated by the service layer, persisted in `reviews.review_json`, rendered in the UI, and covered by tests.

## 14. Next Step

Next v0.2.15 should add review export: generate a local Markdown or HTML monthly report from a saved snapshot, including score summary, decision drill-down, rule results, violations, evidence references, and next-month forbidden behaviors.

### v0.2.15 Review Snapshot Export

- Add a Markdown export service for saved monthly review snapshots.
- Generate local report files under `data/reports/`.
- Include score summary, status counts, violation types, attribution, rule revision suggestions, next-month forbidden behaviors, decision drill-down, rule results, violations, and evidence references.
- Add `/api/reviews/export` endpoint.
- Add an `Export Markdown` action to each saved review snapshot in the Monthly Review UI.
- Add regression coverage for report file generation and report content.

Acceptance: after saving a review snapshot, the user can export it from the UI and receive a local Markdown report path that remains readable outside the app.

Status: completed. Markdown report export is implemented through service, API, UI, and tests.

## 15. Next Step

Next v0.2.16 should add snapshot comparison: select two saved review snapshots and compare score, status counts, violation types, rule suggestions, and repeated symbols to show whether discipline is improving or deteriorating over time.

### v0.2.16 Review Snapshot Comparison

- Add a service method to compare two saved monthly review snapshots.
- Compare discipline score, pass rate, decision count, violation weight, status counts, and violation types.
- Detect repeated symbols with violations across both snapshots.
- Compare rule revision suggestions as persistent, added, and removed.
- Add `/api/reviews/compare` endpoint.
- Add Monthly Review UI controls for selecting baseline and target snapshots.
- Render a comparison summary with trend interpretation and detailed deltas.

Acceptance: after saving at least two review snapshots, the user can select a baseline and target snapshot, compare them, and see whether discipline metrics improved, deteriorated, or stayed mixed.

Status: completed. Snapshot comparison is implemented through service, API, UI, and regression tests.

## 16. Next Step

Next v0.2.17 should add report indexing: list previously exported Markdown reports in the UI, show file path/size/created time, and allow regenerating a report from an existing snapshot without searching the filesystem manually.

### v0.2.17 Review Report Index

- Add service support for scanning `data/reports/*.md`.
- Parse exported report metadata, including title, period, and full snapshot id.
- Add `/api/reports` endpoint.
- Include recent report index entries in the dashboard payload.
- Add a Report Library section to Monthly Review UI.
- Show report path, size, modified time, and snapshot id.
- Allow regenerating a report from the indexed snapshot id.
- Add regression coverage for report indexing.

Acceptance: after exporting review reports, the user can see them in the UI without opening the filesystem and can regenerate a report from an indexed snapshot.

Status: completed. Report indexing is implemented through service, API, dashboard, UI, and tests.

## 17. Next Step

Next v0.2.18 should add local data backup and restore: export the SQLite-backed working set and JSON legacy files into a timestamped archive, then provide a restore flow for moving DisciplineOS data between machines.

### v0.2.18 Local Backup and Restore

- Add timestamped local backup archives under `data/backups/`.
- Include SQLite database, JSON legacy/export files, reports, and local data artifacts.
- Exclude the `backups/` directory from backup archives to avoid recursive archives.
- Add a backup manifest with created time and file list.
- Add restore support with zip entry path validation.
- Add `/api/backups` GET/POST endpoints and `/api/backups/restore`.
- Add Settings UI controls for creating, listing, and restoring backups.
- Add regression coverage for backup round-trip and unsafe archive rejection.

Acceptance: the user can create a local backup from the UI, see it in the backup list, and restore it later without manually copying files.

Status: completed. Backup creation, backup listing, restore validation, Web API, UI, and tests are implemented.

## 18. Next Step

Next v0.2.19 should add a data health check: scan storage, snapshots, reports, backups, provider mappings, and rule-result consistency, then surface warnings in the UI before the user relies on a review report.

### v0.2.19 Data Health Check

- Add service-level health checks for SQLite database presence.
- Check decision/audit linkage, audited decisions without rule results, orphan rule results, and orphan violations.
- Check review snapshots for missing drill-down payloads.
- Check exported reports for missing snapshot references.
- Check whether at least one local backup exists.
- Check capability mappings that reference missing providers and enabled providers with blocked/error status.
- Add `/api/health` endpoint.
- Include health status in dashboard payload.
- Add Settings UI health panel with PASS/WARN/BLOCKED checks.
- Add regression coverage for backup warnings and missing snapshot report warnings.

Acceptance: the user can open the app and immediately see whether local data is healthy enough to trust review reports and exports.

Status: completed. Data health checks are implemented through service, API, dashboard, UI, and tests.

## 19. Next Step

Next v0.2.20 should add import/export hardening: validate CSV/Excel import schemas before writing, preview row counts and errors, and let the user confirm imports from Data Source Center.

### v0.2.20 Import Preview and Confirmation

- Add required-column validation for CSV/Excel imports before any data is written.
- Return row count, valid count, skipped count, missing columns, errors, and sample normalized rows.
- Add non-writing import preview flow for manual file imports.
- Add non-writing preview flow for Data Source Center capability sync.
- Require explicit user confirmation before writing previewed positions or trades.
- Preserve existing commit path for CLI/API automation.
- Add `/api/import-preview` endpoint and `confirm` support on `/api/import` and `/api/data-sync`.
- Add UI preview and confirm actions for Data Import and mapped-provider sync.
- Add regression coverage for preview-only imports, missing required columns, and sync preview.

Acceptance: CSV/Excel data can be inspected before writing; malformed files report schema errors without modifying positions or trades; mapped-provider sync follows the same preview/confirm path.

Status: completed. Import hardening is implemented through adapters, service layer, Web API, UI, and tests.

## 20. Next Step

Next v0.2.21 should add real connector interfaces: define a provider connector protocol and implement the first non-manual market-data connector path behind Data Source Center without changing Decision Gate behavior.

### v0.2.21 Provider Connector Interface

- Add a connector protocol and executable CSV/Excel connector layer.
- Route Data Source Center sync through connector objects instead of hard-coded positions/trades branching.
- Preserve positions/trades import behavior through the connector path.
- Add first non-manual market-data sync path for `price_daily`, `volume`, and `financial_metrics`.
- Convert synced market data into Evidence Engine items without changing Rule Engine final decision behavior.
- Support preview/confirm semantics for connector-backed market data sync.
- Add UI sync capability options for price, volume, and financial metrics.
- Add regression coverage for connector preview, confirmed evidence creation, and schema rejection.

Acceptance: a CSV/Excel provider mapped to `price_daily` can be previewed and then confirmed from Data Source Center, producing `price_condition` evidence items that Decision Gate can later reference.

Status: completed. Connector protocol, CSV/Excel connector, market evidence sync, UI options, and tests are implemented.

## 21. Next Step

Next v0.2.22 should add richer normalized market-data storage: persist raw/normalized price and volume rows separately from evidence summaries, so future review and charting can inspect time series without overloading evidence items.

