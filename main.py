import streamlit as st
st.title('김똥구우ㅜㅜㅜㅜㅜ')
a=st.text_input('이름을 입력하세요!')
b=st.selectbox('좋아하는 별명을 선택하세요',['김똥구','김동구','동동이'])
if st.button('인사말 생성'):
  st.write('반갑습니다')
  st.info(a+'님 안녕하세요!!!!!!!!!!!!!!!!!!!')
  st.warning(b+'좋아하시는군요!')
  st.error('제제야')
  st.balloons()
