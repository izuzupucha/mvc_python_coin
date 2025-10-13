import streamlit as st

class OrderFormView:
    # Hàm giả định tính toán SL/TP (BẠN CẦN THAY THẾ BẰNG LOGIC CỦA MÌNH)
    @staticmethod
    def calculate_sl_tp(order_type: str, current_price: float):
        """
        Tính toán SL và TP dựa trên giá hiện tại.
        NOTE: Thay thế bằng logic tính toán thực tế (ví dụ: dùng ATR, R:R cố định, v.v.).
        """
        if order_type == 'long':
            # Long: SL thấp hơn, TP cao hơn
            stop_loss = current_price * 0.99  # Giả định: SL 1% dưới giá Entry
            take_profit = current_price * 1.02  # Giả định: TP 2% trên giá Entry
        else: # short
            # Short: SL cao hơn, TP thấp hơn
            stop_loss = current_price * 1.01  # Giả định: SL 1% trên giá Entry
            take_profit = current_price * 0.98  # Giả định: TP 2% dưới giá Entry
            
        # Làm tròn giá trị để dễ nhìn
        return round(stop_loss, 2), round(take_profit, 2)

    @staticmethod
    def show(order_type: str, coin_pair: str):
        st.subheader(f"💰 Đặt lệnh {'MUA (Long)' if order_type == 'long' else 'BÁN (Short)'} cho {coin_pair}")
        
        # Thiết lập giá trị mặc định cho session_state (để tránh lỗi)
        if "calculated_entry" not in st.session_state:
             st.session_state["calculated_entry"] = 100.0
        if "calculated_sl" not in st.session_state:
             st.session_state["calculated_sl"] = 95.0
        if "calculated_tp" not in st.session_state:
             st.session_state["calculated_tp"] = 110.0
        if "auto_calculate_prices" not in st.session_state:
             st.session_state["auto_calculate_prices"] = False

        with st.form("order_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                # Thao tác nhập Vốn và Rủi ro
                capital = st.number_input("💵 Tổng vốn (USD)", min_value=10.0, value=1000.0, step=10.0, key="order_capital")
                risk_percent = st.number_input("⚠️ Tỷ lệ rủi ro (%)", min_value=0.1, max_value=100.0, value=2.0, step=0.5, key="order_risk_percent")
            
            with col2:
                # 1️⃣ INPUT/CALCULATE ENTRY PRICE
                # Giả định nhập giá hiện tại (Entry)
                # Dùng một key khác để giá Entry có thể được cập nhật mà không bị reset khi checkbox được bấm
                current_entry = st.number_input(
                    "🎯 Giá vào lệnh (Entry)", 
                    min_value=0.0, 
                    value=st.session_state["calculated_entry"], 
                    step=0.1, 
                    key="entry_price_input"
                )
                
                # 2️⃣ CHECKBOX TỰ ĐỘNG TÍNH TOÁN
                # Bật/tắt chế độ tự động tính toán SL/TP
                auto_calculate = st.checkbox(
                    "✨ Tự động tính SL/TP",
                    value=st.session_state["auto_calculate_prices"],
                    key="auto_calculate_prices_checkbox"
                )
            
            # Cập nhật giá trị SL/TP nếu checkbox được chọn
            if auto_calculate:
                # Lưu giá Entry hiện tại để dùng cho lần sau
                st.session_state["calculated_entry"] = current_entry
                
                # Tính toán SL/TP dựa trên Entry
                calculated_sl, calculated_tp = OrderFormView.calculate_sl_tp(order_type, current_entry)
                
                st.session_state["calculated_sl"] = calculated_sl
                st.session_state["calculated_tp"] = calculated_tp
                
                # Hiển thị SL và TP đã được tính toán (chỉ để xem, không cho chỉnh sửa)
                stop_loss = st.number_input(
                    "🛑 Giá cắt lỗ (SL) (Tự động)", 
                    min_value=0.0, 
                    value=calculated_sl, 
                    step=0.1, 
                    disabled=True,
                    key="sl_display"
                )
                take_profit = st.number_input(
                    "🏁 Giá chốt lời (TP) (Tự động)", 
                    min_value=0.0, 
                    value=calculated_tp, 
                    step=0.1, 
                    disabled=True,
                    key="tp_display"
                )
                st.info(f"SL/TP được tính tự động dựa trên Entry `{current_entry}`")
                
            else:
                # 3️⃣ NHẬP THỦ CÔNG SL/TP
                # Nếu không chọn tự động, cho phép nhập thủ công
                stop_loss = st.number_input(
                    "🛑 Giá cắt lỗ (SL)", 
                    min_value=0.0, 
                    value=st.session_state.get("calculated_sl", 95.0), 
                    step=0.1,
                    key="sl_manual"
                )
                take_profit = st.number_input(
                    "🏁 Giá chốt lời (TP)", 
                    min_value=0.0, 
                    value=st.session_state.get("calculated_tp", 110.0), 
                    step=0.1,
                    key="tp_manual"
                )

            submitted = st.form_submit_button("✅ Xác nhận đặt lệnh")

        # Lưu trạng thái checkbox
        st.session_state["auto_calculate_prices"] = auto_calculate

        # Lấy giá Entry cuối cùng để tính toán
        entry_price = current_entry

        # ✅ Tính toán khi bấm submit
        if submitted:
            try:
                # 1️⃣ Số tiền rủi ro
                risk_amount = capital * (risk_percent / 100.0)

                # 2️⃣ Khoảng cách từ entry đến SL
                diff = abs(entry_price - stop_loss)

                if diff == 0:
                    st.error("❌ Giá vào lệnh và SL không được trùng nhau.")
                    return
                
                if order_type == 'long' and entry_price <= stop_loss:
                    st.error("❌ Lệnh MUA (Long): Giá SL phải thấp hơn giá Entry.")
                    return
                
                if order_type == 'short' and entry_price >= stop_loss:
                    st.error("❌ Lệnh BÁN (Short): Giá SL phải cao hơn giá Entry.")
                    return

                # 3️⃣ Khối lượng lệnh (volume)
                volume = risk_amount / diff

                # 4️⃣ Tỷ lệ Risk/Reward
                rr_ratio = abs(take_profit - entry_price) / diff if diff != 0 else 0

                # ✅ Hiển thị kết quả
                st.success(
                    f"**Kết quả tính toán**\n"
                    f"- Vốn: `${capital:,.2f}`\n"
                    f"- Rủi ro: `{risk_percent:.2f}%` → `${risk_amount:,.2f}`\n"
                    f"- Khối lượng lệnh: **{volume:.4f} {coin_pair.replace('USDT', '')}**\n"
                    f"- Tỷ lệ R:R = `{rr_ratio:.2f}`\n"
                )

                st.info(f"Lệnh {order_type.upper()} — Entry `{entry_price}`, SL `{stop_loss}`, TP `{take_profit}`")

                if st.button("🔙 Quay lại", key="back_button_after_submit"):
                    del st.session_state["show_order_form"]
                    st.rerun()

            except Exception as e:
                st.error(f"⚠️ Lỗi khi tính toán lệnh: {e}")