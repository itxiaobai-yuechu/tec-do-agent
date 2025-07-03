# -*- coding: utf-8 -*-
import gradio as gr
from config import logger, conf

from src.config import (
    http_proxy,
    hide_history_when_not_logged_in,
    chat_name_method_index,
    my_api_key,
    multi_api_key,
    server_name,
    server_port,
    share,
    config_file,
    api_host,
    authflag,
    dockerflag,
    show_api_billing,
    latex_delimiters_set,
    user_avatar,
    bot_avatar,
    autobrowser,
    update_doc_config,
)
from src.gradio_patch import reg_patch
from src.overwrites import (
    postprocess,
    postprocess_chat_messages,
    reload_javascript,
    get_html,
)
from src.presets import (
    MODELS,
    HISTORY_NAME_METHODS,
    small_and_beautiful_theme,
    CONCURRENT_COUNT,
    TITLE,
    HIDE_MY_KEY,
    DEFAULT_MODEL,
    REPLY_LANGUAGES,
    INITIAL_SYSTEM_PROMPT,
    ENABLE_STREAMING_OPTION,
    DESCRIPTION,
    favicon_path,
    API_HOST,
    HISTORY_DIR,
    assets_path,
)
from src.utils import (
    delete_chat_history,
    filter_history,
    get_history_list,
    auto_name_chat_history,
    get_template_dropdown,
    rename_chat_history,
    init_history_list,
    get_first_history_name,
    setup_wizard,
    auth_from_conf,
    get_geoip,
    get_template_names,
    load_template,
    get_history_names,
    predict,
    interrupt,
    retry,
    i18n,
    dislike,
    toggle_like_btn_visibility,
    set_key,
    set_single_turn,
    hide_middle_chars,
    set_system_prompt,
    start_outputing,
    set_token_upper_limit,
    set_temperature,
    set_user_identifier,
    set_top_p,
    delete_first_conversation,
    delete_last_conversation,
    set_n_choices,
    set_logit_bias,
    end_outputing,
    set_max_tokens,
    reset_default,
    reset_textbox,
    set_stop_sequence,
    set_presence_penalty,
    set_frequency_penalty,
    upload_chat_history,
    export_markdown,
    billing_info,
    get_template_content,
    like,
    transfer_input,
    handle_file_upload,
    handle_summarize_index,
    set_language_by_country
)
from src.hook import load_app, reset, load_chat_history
reg_patch()

gr.Chatbot._postprocess_chat_messages = postprocess_chat_messages
gr.Chatbot.postprocess = postprocess


def load(user_name, user_info):

    user_info = gr.Markdown(
        value=user_info, elem_id="user-info")
    with gr.Blocks(theme=small_and_beautiful_theme) as demo:
        # 激活/logout路由
        user_name = gr.Textbox(value=user_name, visible=False)
        logout_hidden_btn = gr.LogoutButton(visible=False)
        promptTemplates = gr.State(
            load_template(get_template_names()[0], mode=2))
        user_question = gr.State("")
        assert type(my_api_key) == str
        user_api_key = gr.State(my_api_key)
        current_help_model = gr.State()
        language = set_language_by_country(get_geoip())
        topic = gr.State(i18n("未命名对话历史记录"))

        # TODO 根据IP来设置默认语言，关键函数：get_geoip()
        with gr.Row(elem_id="tecdo-header"):
            gr.HTML(get_html("header_title.html").format(
                app_title=TITLE), elem_id="app-title")
            # 状态：一般为放置IP处
            status_display = gr.Markdown(get_geoip, elem_id="status-display")
        with gr.Row(elem_id="float-display"):
            user_info.render()
        with gr.Row(equal_height=True, elem_id="tecdo-body"):
            with gr.Column(elem_id="menu-area"):
                with gr.Column(elem_id="tecdo-history"):
                    with gr.Box():
                        with gr.Row(elem_id="tecdo-history-header"):
                            with gr.Row(elem_id="tecdo-history-search-row"):
                                with gr.Column(min_width=150, scale=2):
                                    historySearchTextbox = gr.Textbox(show_label=False, container=False, placeholder=i18n(
                                        "搜索（支持正则）..."), lines=1, elem_id="history-search-tb")
                                with gr.Column(min_width=52, scale=1, elem_id="gr-history-header-btns"):
                                    uploadFileBtn = gr.UploadButton(
                                        interactive=True, label="", file_types=[".json"], elem_id="gr-history-upload-btn")
                                    historyRefreshBtn = gr.Button(
                                        "", elem_id="gr-history-refresh-btn")

                        with gr.Row(elem_id="tecdo-history-body"):
                            with gr.Column(scale=6, elem_id="history-select-wrap"):
                                historySelectList = gr.Radio(
                                    label=i18n("从列表中加载对话"),
                                    choices=get_history_names(
                                        user_name=str(user_name.value)),
                                    value=get_first_history_name(
                                        user_name=str(user_name.value)),
                                    # multiselect=False,
                                    container=False,
                                    elem_id="history-select-dropdown"
                                )
                            with gr.Row(visible=False):
                                with gr.Column(min_width=42, scale=1):
                                    # 删除对话按钮
                                    historyDeleteBtn = gr.Button(
                                        "🗑️", elem_id="gr-history-delete-btn")
                                with gr.Column(min_width=42, scale=1):
                                    historyDownloadBtn = gr.Button(
                                        "⏬", elem_id="gr-history-download-btn")
                                with gr.Column(min_width=42, scale=1):
                                    historyMarkdownDownloadBtn = gr.Button(
                                        "⤵️", elem_id="gr-history-mardown-download-btn")
                        with gr.Row(visible=False):
                            with gr.Column(scale=6):
                                saveFileName = gr.Textbox(
                                    show_label=True,
                                    placeholder=i18n("设置文件名: 默认为.json，可选为.md"),
                                    label=i18n("设置保存文件名"),
                                    value=i18n("对话历史记录"),
                                    elem_classes="no-container"
                                    # container=False,
                                )
                            with gr.Column(scale=1):
                                renameHistoryBtn = gr.Button(
                                    i18n("💾 保存对话"), elem_id="gr-history-save-btn")
                                exportMarkdownBtn = gr.Button(
                                    i18n("📝 导出为 Markdown"), elem_id="gr-markdown-export-btn")

                with gr.Column(elem_id="tecdo-menu-footer"):
                    with gr.Row(elem_id="tecdo-func-nav"):
                        gr.HTML(get_html("func_nav.html"))
                    # gr.HTML(get_html("footer.html").format(versions=versions_html()), elem_id="footer")
                    # gr.Markdown(tecdo_DESCRIPTION, elem_id="tecdo-author")

            with gr.Column(elem_id="tecdo-area", scale=5):
                with gr.Column(elem_id="chatbot-area"):
                    with gr.Row(elem_id="chatbot-header"):
                        # # 模型选择
                        # model_select_dropdown = gr.Dropdown(
                        #     label=i18n("选择模型"), choices=MODELS, multiselect=False, value=MODELS[DEFAULT_MODEL],
                        #     interactive=True,
                        #     show_label=False, container=False, elem_id="model-select-dropdown"
                        # )
                        gr.HTML(get_html("chatbot_header_btn.html").format(
                            json_label=i18n("历史记录（JSON）"),
                            md_label=i18n("导出为 Markdown")
                        ), elem_id="chatbot-header-btn-bar")
                    with gr.Row():
                        chatbot = gr.Chatbot(
                            label="ChatGPT",
                            elem_id="tecdo-chatbot",
                            latex_delimiters=latex_delimiters_set,
                            sanitize_html=False,
                            # height=700,
                            show_label=False,
                            avatar_images=(user_avatar, bot_avatar),
                            show_share_button=False,
                        )
                    with gr.Row(elem_id="chatbot-footer"):
                        with gr.Box(elem_id="chatbot-input-box"):
                            with gr.Row(elem_id="chatbot-input-row"):
                                gr.HTML(get_html("chatbot_more.html").format(
                                    single_turn_label=i18n("单轮对话"),
                                    websearch_label=i18n("在线搜索"),
                                    upload_file_label=i18n("上传文件"),
                                    uploaded_files_label=i18n("知识库文件"),
                                    uploaded_files_tip=i18n("在工具箱中管理知识库文件")
                                ))
                                with gr.Row(elem_id="chatbot-input-tb-row"):
                                    with gr.Column(min_width=225, scale=12):
                                        user_input = gr.Textbox(
                                            elem_id="user-input-tb",
                                            show_label=False,
                                            placeholder=i18n("在这里输入"),
                                            elem_classes="no-container",
                                            max_lines=5,
                                            # container=False
                                        )
                                    with gr.Column(min_width=42, scale=1, elem_id="chatbot-ctrl-btns"):
                                        submitBtn = gr.Button(
                                            value="", variant="primary", elem_id="submit-btn")
                                        cancelBtn = gr.Button(
                                            value="", variant="secondary", visible=False, elem_id="cancel-btn")
                            # Note: Buttons below are set invisible in UI. But they are used in JS.
                            with gr.Row(elem_id="chatbot-buttons", visible=False):
                                with gr.Column(min_width=120, scale=1):
                                    # emptyBtn ->创建新对话
                                    emptyBtn = gr.Button(
                                        i18n("🧹 新的对话"), elem_id="empty-btn"
                                    )
                                with gr.Column(min_width=120, scale=1):
                                    retryBtn = gr.Button(
                                        i18n("🔄 重新生成"), elem_id="gr-retry-btn")
                                with gr.Column(min_width=120, scale=1):
                                    delFirstBtn = gr.Button(i18n("🗑️ 删除最旧对话"))
                                with gr.Column(min_width=120, scale=1):
                                    delLastBtn = gr.Button(
                                        i18n("🗑️ 删除最新对话"), elem_id="gr-dellast-btn")
                                with gr.Row(visible=False) as like_dislike_area:
                                    with gr.Column(min_width=20, scale=1):
                                        likeBtn = gr.Button(
                                            "👍", elem_id="gr-like-btn")
                                    with gr.Column(min_width=20, scale=1):
                                        dislikeBtn = gr.Button(
                                            "👎", elem_id="gr-dislike-btn")

            with gr.Column(elem_id="toolbox-area", scale=1):
                # For CSS setting, there is an extra box. Don't remove it.
                with gr.Box(elem_id="tecdo-toolbox"):
                    with gr.Row():
                        gr.Markdown("## " + i18n("工具箱"))
                        gr.HTML(get_html("close_btn.html").format(
                            obj="toolbox"), elem_classes="close-btn")
                    with gr.Tabs(elem_id="tecdo-toolbox-tabs"):
                        with gr.Tab(label=i18n("商品展示界面")):
                            # gr.Markdown("### " + i18n("商品标题"))
                            gr.Textbox(placeholder="商品标题", label="商品标题",
                                       show_label=True, interactive=True, elem_id="product_title", type="text")
                            gr.Textbox(placeholder="商品介绍", label="商品介绍",
                                       show_label=True, interactive=True, elem_id="product_description", type="text")

                        with gr.Tab(label=i18n("参数")):
                            gr.Markdown(i18n("# ⚠️ 务必谨慎更改 "),
                                        elem_id="advanced-warning")
                            with gr.Accordion(i18n("参数"), open=True):
                                temperature_slider = gr.Slider(
                                    minimum=-0,
                                    maximum=2.0,
                                    value=1.0,
                                    step=0.1,
                                    interactive=True,
                                    label="temperature",
                                )
                                # top_p_slider = gr.Slider(
                                #     minimum=-0,
                                #     maximum=1.0,
                                #     value=1.0,
                                #     step=0.05,
                                #     interactive=True,
                                #     label="top-p",
                                # )
                                # n_choices_slider = gr.Slider(
                                #     minimum=1,
                                #     maximum=10,
                                #     value=1,
                                #     step=1,
                                #     interactive=True,
                                #     label="n choices",
                                # )
                                # stop_sequence_txt = gr.Textbox(
                                #     show_label=True,
                                #     placeholder=i18n("停止符，用英文逗号隔开..."),
                                #     label="stop",
                                #     value="",
                                #     lines=1,
                                # )
                                # max_context_length_slider = gr.Slider(
                                #     minimum=1,
                                #     maximum=32768,
                                #     value=2000,
                                #     step=1,
                                #     interactive=True,
                                #     label="max context",
                                # )
                                # max_generation_slider = gr.Slider(
                                #     minimum=1,
                                #     maximum=32768,
                                #     value=1000,
                                #     step=1,
                                #     interactive=True,
                                #     label="max generations",
                                # )
                                # presence_penalty_slider = gr.Slider(
                                #     minimum=-2.0,
                                #     maximum=2.0,
                                #     value=0.0,
                                #     step=0.01,
                                #     interactive=True,
                                #     label="presence penalty",
                                # )
                                # frequency_penalty_slider = gr.Slider(
                                #     minimum=-2.0,
                                #     maximum=2.0,
                                #     value=0.0,
                                #     step=0.01,
                                #     interactive=True,
                                #     label="frequency penalty",
                                # )
                                # logit_bias_txt = gr.Textbox(
                                #     show_label=True,
                                #     placeholder=f"word:likelihood",
                                #     label="logit bias",
                                #     value="",q
                                #     lines=1,
                                # )
                                # user_identifier_txt = gr.Textbox(
                                #     show_label=True,
                                #     placeholder=i18n("用于定位滥用行为"),
                                #     label=i18n("用户标识符"),
                                #     value=str(user_name.value),
                                #     lines=1,
                                # )

        with gr.Row(elem_id="popup-wrapper"):
            with gr.Box(elem_id="tecdo-popup"):
                with gr.Box(elem_id="tecdo-setting"):
                    with gr.Row():
                        gr.Markdown("## " + i18n("设置"))
                        gr.HTML(get_html("close_btn.html").format(
                            obj="box"), elem_classes="close-btn")
                    with gr.Tabs(elem_id="tecdo-setting-tabs"):
                        with gr.Tab(label=i18n("高级")):
                            gr.HTML(get_html("appearance_switcher.html").format(
                                label=i18n("切换亮暗色主题")), elem_classes="insert-block", visible=False)
                            use_streaming_checkbox = gr.Checkbox(
                                label=i18n("实时传输回答"), value=True, visible=ENABLE_STREAMING_OPTION,
                                elem_classes="switch-checkbox"
                            )
                            name_chat_method = gr.Dropdown(
                                label=i18n("对话命名方式"),
                                choices=HISTORY_NAME_METHODS,
                                multiselect=False,
                                interactive=True,
                                value=HISTORY_NAME_METHODS[chat_name_method_index],
                            )
                            single_turn_checkbox = gr.Checkbox(label=i18n(
                                "单轮对话"), value=False, elem_classes="switch-checkbox", elem_id="gr-single-session-cb",
                                visible=False)
                            # checkUpdateBtn = gr.Button(i18n("🔄 检查更新..."), visible=check_update)
                            logout_btn = gr.Button(
                                i18n("退出用户"), variant="primary", visible=authflag)

                        with gr.Tab(i18n("语言")):
                            with gr.Accordion(i18n("language"), open=True):
                                language_select_dropdown = gr.Dropdown(
                                    label=i18n("选择回复语言（针对搜索&索引功能）"),
                                    choices=REPLY_LANGUAGES,
                                    multiselect=False,
                                    value=REPLY_LANGUAGES[0],
                                    visible=False,
                                )
                        # with gr.Tab(i18n("网络")):
                        #     gr.Markdown(
                        #         i18n("⚠️ 为保证API-Key安全，请在配置文件`config.json`中修改网络设置"),
                        #         elem_id="netsetting-warning")
                        #     default_btn = gr.Button(i18n("🔙 恢复默认网络设置"))
                        #     # 网络代理
                        #     proxyTxt = gr.Textbox(
                        #         show_label=True,
                        #         placeholder=i18n("未设置代理..."),
                        #         label=i18n("代理地址"),
                        #         value=http_proxy,
                        #         lines=1,
                        #         interactive=False,
                        #         # container=False,
                        #         elem_classes="view-only-textbox no-container",
                        #     )
                            # changeProxyBtn = gr.Button(i18n("🔄 设置代理地址"))

                            # 优先展示自定义的api_host
                            # apihostTxt = gr.Textbox(
                            #     show_label=True,
                            #     placeholder="api.openai.com",
                            #     label="OpenAI API-Host",
                            #     value=api_host or API_HOST,
                            #     lines=1,
                            #     interactive=False,
                            #     # container=False,
                            #     elem_classes="view-only-textbox no-container",
                            # )
                with gr.Box(elem_id="web-config", visible=False):
                    gr.HTML(get_html('web_config.html').format(
                        enableCheckUpdate_config=False,
                        hideHistoryWhenNotLoggedIn_config=hide_history_when_not_logged_in,
                        forView_i18n=i18n("仅供查看"),
                        deleteConfirm_i18n_pref=i18n("你真的要删除 "),
                        deleteConfirm_i18n_suff=i18n(" 吗？"),
                        usingLatest_i18n=i18n("您使用的就是最新版！"),
                        updatingMsg_i18n=i18n("正在尝试更新..."),
                        updateSuccess_i18n=i18n("更新成功，请重启本程序"),
                        updateFailure_i18n=i18n(
                            "更新失败，请尝试[手动更新](https://github.com/shibing624/chatgpt-webui/"),
                        regenerate_i18n=i18n("重新生成"),
                        deleteRound_i18n=i18n("删除这轮问答"),
                        renameChat_i18n=i18n("重命名该对话"),
                        validFileName_i18n=i18n("请输入有效的文件名，不要包含以下特殊字符："),
                        clearFileHistoryMsg_i18n=i18n(
                            "⚠️请先删除知识库中的历史文件，再尝试上传！"),
                        dropUploadMsg_i18n=i18n("释放文件以上传"),
                    ))
                with gr.Box(elem_id="fake-gradio-components", visible=False):
                    changeSingleSessionBtn = gr.Button(
                        visible=False, elem_classes="invisible-btn", elem_id="change-single-session-btn")
                    changeOnlineSearchBtn = gr.Button(
                        visible=False, elem_classes="invisible-btn", elem_id="change-online-search-btn")
                    historySelectBtn = gr.Button(
                        visible=False, elem_classes="invisible-btn", elem_id="history-select-btn")  # Not used

        # TODO : 应用加载后的第一个程序
        demo.load(load_app, inputs=[user_name], outputs=[
            current_help_model], api_name="load")

        chatgpt_predict_args = dict(
            fn=predict,
            inputs=[
                user_question,
                chatbot,
                use_streaming_checkbox,
                language_select_dropdown,
            ],
            outputs=[chatbot],
            show_progress="full",
        )

        start_outputing_args = dict(
            fn=start_outputing,
            inputs=[],
            outputs=[submitBtn, cancelBtn],
            show_progress="full",
        )

        end_outputing_args = dict(
            fn=end_outputing, inputs=[], outputs=[submitBtn, cancelBtn]
        )

        reset_textbox_args = dict(
            fn=reset_textbox, inputs=[], outputs=[user_input]
        )

        transfer_input_args = dict(
            fn=transfer_input, inputs=[user_input], outputs=[
                user_question, user_input, submitBtn, cancelBtn], show_progress="full"
        )

        # get_usage_args = dict(
        #     fn=billing_info, inputs=[current_help_model], outputs=[
        #         usageTxt], show_progress="hidden"
        # )

        load_history_from_file_args = dict(
            fn=load_chat_history,
            inputs=[historySelectList, user_name],
            outputs=[saveFileName,  chatbot],
        )

        refresh_history_args = dict(
            fn=get_history_list, inputs=[
                user_name], outputs=[historySelectList]
        )

        auto_name_chat_history_args = dict(
            fn=auto_name_chat_history,
            inputs=[current_help_model, name_chat_method,
                    chatbot, single_turn_checkbox],
            outputs=[historySelectList],
            show_progress="hidden",
        )

        # Chatbot
        cancelBtn.click(interrupt, [current_help_model], [])

        user_input.submit(
            **transfer_input_args).then(
            **chatgpt_predict_args).then(
            **end_outputing_args).then(
            **auto_name_chat_history_args)
        # user_input.submit(**get_usage_args)

        # submitBtn.click(**transfer_input_args).then(
        #     **chatgpt_predict_args, api_name="predict").then(
        #     **end_outputing_args).then(
        #     **auto_name_chat_history_args)
        # submitBtn.click(**get_usage_args)

        # TODO 创建新对话按钮的完善
        emptyBtn.click(
            reset,
            inputs=[user_name],
            outputs=[chatbot, historySelectList],
            show_progress="full",
            _js='(a,b)=>{return clearChatbot(a,b);}',
        )

        # retryBtn.click(**start_outputing_args).then(
        #     retry,
        #     [
        #         current_help_model,
        #         chatbot,
        #         use_streaming_checkbox,
        #         use_websearch_checkbox,
        #         index_files,
        #         language_select_dropdown,
        #     ],
        #     [chatbot, status_display],
        #     show_progress="full",
        # ).then(**end_outputing_args)
        # retryBtn.click(**get_usage_args)

        delFirstBtn.click(
            delete_first_conversation,
            [current_help_model],
            [status_display],
        )

        delLastBtn.click(
            delete_last_conversation,
            [current_help_model, chatbot],
            [chatbot, status_display],
            show_progress="hidden"
        )

        likeBtn.click(
            like,
            [current_help_model],
            [status_display],
            show_progress="hidden"
        )

        dislikeBtn.click(
            dislike,
            [current_help_model],
            [status_display],
            show_progress="hidden"
        )
        single_turn_checkbox.change(
            set_single_turn, [current_help_model, single_turn_checkbox], None, show_progress="hidden")
        # model_select_dropdown.change(get_model,
        #                              [model_select_dropdown, lora_select_dropdown, user_api_key, temperature_slider,
        #                               top_p_slider, systemPromptTxt, user_name, current_help_model], [
        #                                  current_help_model, status_display, chatbot, lora_select_dropdown, user_api_key,
        #                                  keyTxt], show_progress="full", api_name="get_model")
        # model_select_dropdown.change(toggle_like_btn_visibility, [model_select_dropdown], [
        #     like_dislike_area], show_progress="hidden")
        # Template
        # S&L

        # 重命名对话
        renameHistoryBtn.click(
            rename_chat_history,
            [current_help_model, saveFileName, chatbot],
            [historySelectList],
            show_progress="full",
            _js='(a,b,c,d)=>{return saveChatHistory(a,b,c,d);}'
        )
        exportMarkdownBtn.click(
            export_markdown,
            [current_help_model, saveFileName, chatbot],
            [],
            show_progress="full",
        )
        historyRefreshBtn.click(**refresh_history_args)
        # historyDeleteBtn.click(delete_chat_history, [current_help_model, historySelectList],
        #                        [status_display, historySelectList, chatbot],
        #                        _js='(a,b,c)=>{return showConfirmationDialog(a, b, c);}').then(
        #     reset,
        #     inputs=[current_help_model, retain_system_prompt_checkbox],
        #     outputs=[chatbot, status_display, historySelectList, systemPromptTxt],
        #     show_progress="full",
        #     _js='(a,b)=>{return clearChatbot(a,b);}',
        # )
        historySelectList.input(**load_history_from_file_args)
        # uploadFileBtn.upload(upload_chat_history, [current_help_model, uploadFileBtn], [
        #     saveFileName, systemPromptTxt, chatbot, single_turn_checkbox, temperature_slider, top_p_slider,
        #     n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider, presence_penalty_slider,
        #     frequency_penalty_slider, logit_bias_txt, user_identifier_txt]).then(**refresh_history_args)
        historyDownloadBtn.click(None, [
            user_name, historySelectList], None, _js='(a,b)=>{return downloadHistory(a,b,".json");}')
        historyMarkdownDownloadBtn.click(None, [
            user_name, historySelectList], None, _js='(a,b)=>{return downloadHistory(a,b,".md");}')
        historySearchTextbox.input(
            filter_history,
            [user_name, historySearchTextbox],
            [historySelectList]
        )

        # Advanced
        temperature_slider.input(
            set_temperature, [current_help_model, temperature_slider], None, show_progress="hidden")
        # top_p_slider.input(
        #     set_top_p, [current_help_model, top_p_slider], None, show_progress="hidden")
        # n_choices_slider.input(
        #     set_n_choices, [current_help_model, n_choices_slider], None, show_progress="hidden")
        # stop_sequence_txt.input(
        #     set_stop_sequence, [current_help_model, stop_sequence_txt], None, show_progress="hidden")
        # max_context_length_slider.input(
        #     set_token_upper_limit, [current_help_model, max_context_length_slider], None, show_progress="hidden")
        # max_generation_slider.input(
        #     set_max_tokens, [current_help_model, max_generation_slider], None, show_progress="hidden")
        # presence_penalty_slider.input(
        #     set_presence_penalty, [current_help_model, presence_penalty_slider], None, show_progress="hidden")
        # frequency_penalty_slider.input(
        #     set_frequency_penalty, [current_help_model, frequency_penalty_slider], None, show_progress="hidden")
        # logit_bias_txt.input(
        #     set_logit_bias, [current_help_model, logit_bias_txt], None, show_progress="hidden")
        # user_identifier_txt.input(set_user_identifier, [
        #     current_help_model, user_identifier_txt], None, show_progress="hidden")

        # default_btn.click(
        #     reset_default, [], [apihostTxt, proxyTxt, status_display], show_progress="full"
        # )

        # Invisible elements
        changeSingleSessionBtn.click(
            fn=lambda value: gr.Checkbox.update(value=value),
            inputs=[single_turn_checkbox],
            outputs=[single_turn_checkbox],
            _js='(a)=>{return bgChangeSingleSession(a);}'
        )
        # historySelectBtn.click(  # This is an experimental feature... Not actually used.
        #     fn=load_chat_history,
        #     inputs=[current_help_model, historySelectList],
        #     outputs=[saveFileName, systemPromptTxt, chatbot, single_turn_checkbox, temperature_slider, top_p_slider,
        #              n_choices_slider, stop_sequence_txt, max_context_length_slider, max_generation_slider,
        #              presence_penalty_slider, frequency_penalty_slider, logit_bias_txt, user_identifier_txt],
        #     _js='(a,b)=>{return bgSelectHistory(a,b);}'
        # )
        logout_btn.click(
            fn=None,
            inputs=[],
            outputs=[],
            _js='self.location="/logout"'
        )

    demo.title = TITLE
    return demo


if __name__ == "__main__":
    reload_javascript()
    setup_wizard()
#  在运行前获取用户的信息
    user_name = "tec-do"
    user_info = "tec-do"
    demo = load(user_name, user_info)

    demo.queue(concurrency_count=CONCURRENT_COUNT).launch(
        allowed_paths=[HISTORY_DIR, assets_path],
        server_name=server_name,
        server_port=server_port,
        share=share,
        blocked_paths=[config_file],
        auth=auth_from_conf if authflag else None,
        favicon_path=favicon_path,
        inbrowser=autobrowser and not dockerflag,
    )
