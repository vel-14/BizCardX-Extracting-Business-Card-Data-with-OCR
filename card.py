import easyocr
import cv2
import numpy as np
import PIL
from PIL import Image
import re
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector 
import time

#-------- Setting up page configuration------------------------------
st.set_page_config(layout= "wide",
                   menu_items={'About':"This dashboard app is created by Velmurugan Selvaraj!"}
                   )
st.title(':rainbow[Bizcardx -- Extracting Business Card Data with OCR]')

# ---------------------------------Creating Dashboard----------------------
st.write("")
selected = option_menu(None, ["Home", "Upload & Extract",  "Modify"], 
                        icons=['house', 'cloud-upload', "pencil"], 
                        default_index=0, orientation="horizontal",
                        styles={
                            "nav-link-selected": {"background-color": "blue"},
                            }
                          )

#-----------------connecting to mysql-------------------------------------------

mydb=mysql.connector.connect(host='localhost',
                             user='root',
                             password='Velcharru@1406'
                             )
mycursor=mydb.cursor()
mycursor.execute("Create Database IF NOT EXISTS bizcard")
mycursor.execute("use bizcard")
mycursor.execute('''Create Table IF NOT EXISTS card_info(
                           id INT AUTO_INCREMENT PRIMARY KEY,
                           Card_holder_Name varchar(255),
                           Company_name varchar(255),
                           Designation varchar(255),
                           Contact_number varchar(255),
                           Email varchar(255),
                           Website_url varchar(255),
                           Pincode varchar(255),
                           Address varchar(255),
                           City varchar(255),
                           State varchar(255),
                           image LONGBLOB )
                 ''')


#-----------------------creating homepage of web application--------------------------#                           

if selected=='Home':
    col1,col2=st.columns([3,2.5],gap="large")

    with col1:

        st.subheader(":red[Welcome to the Homepage of Bizcardx]")

        st.subheader(":orange[**Technologies Used:**] Python,easy OCR, Streamlit, SQL, Pandas") 

        st.markdown(":violet[This streamlit web application allows you to upload an image of a business card and use easyOCR to extract the necessary information from it. In this programme, the extracted data can be viewed, changed, or removed. Additionally, users would be able to upload a photo of their business card and save the extracted data to SQL database. Each entry would have its own business card image and extracted data, and the database would be able to store many entries.]")

        st.write(":red[Note:-]:green[ Only business cards are permitted to be used.]")
        
    with col2:
        st.text("")
        st.text("")
        st.text("")
        st.text("")

        card_pic=Image.open(r"/Users/velmurugan/Desktop/velu/python_works/biz_card_project/logos.png")
        st.image(card_pic,width=450)

#----------------------------------creating Upload and extract page--------------------------------------

if selected=='Upload & Extract':
    
    image = st.file_uploader("Choose an image of a business card", type=["jpg", "jpeg", "png"])
    
    if image is not None:
                    
        file_bytes = image.read()
        nparr = np.frombuffer(file_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        col1,col2=st.columns(2)
        
        with col1:
            st.text("")
            st.text("")
            st.image(image,channels='BGR' ,width=450,caption="Uploaded image")
            st.spinner("Extracting...")

        with col2:
            reader=easyocr.Reader(['en'])
            result = reader.readtext(np.array(image), detail=0)

            card = " ".join(result)  #convert to string

            replacing=[
                (';',""),
                (',',''),
                ('.com','com'),
                ('com','.com'),
                ('WWW ','www.'),
                ("www ", "www."),
                ('www', 'www.'),
                ('www.','www'),
                ('wWW','www'),
                ('wwW','www')]
            
            for old, new in replacing:
                card = card.replace(old, new)
                
           #-------Extracting phone number------------
           
            phone_pattern=r"\+*\d{2,3}-\d{3,4}-\d{4}"
            match1=re.findall(phone_pattern,card)
            Phone = ''
            for phone in match1:
                Phone = Phone + ' ' + phone
                card=card.replace(phone,"")
                
           #--------------Extracting pincode--------------
        
            pin_code=r"\d+"
            Pincode = ''
            match2=re.findall(pin_code,card)
            for code in match2:
                if len(code)==6 or len(code)==7:
                    Pincode=Pincode+code
                    card=card.replace(code,"")
            
            #--------------Extracting email id--------------------
            
            email_id=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}\b"
            Email_id = ''
            match3=re.findall(email_id,card)
            for ids in match3:
                Email_id = Email_id + ids
                card=card.replace(ids,'')
                
           ##Extracting web url

            web_url=r"www\.[A-Za-z0-9]+\.[A-Za-z]{2,3}"
            Web_Url = ''
            match4=re.findall(web_url,card)
            for url in match4:
                Web_Url = url + Web_Url
                card=card.replace(url,"")
                
            #-----------Extracting alpha words from the result---------------------

            alpha_patterns = r'^[A-Za-z]+ [A-Za-z]+$|^[A-Za-z]+$|^[A-Za-z]+ & [A-Za-z]+$'
            alpha_var=[]
            for i in result:
                if re.findall(alpha_patterns,i):
                    if i not in 'WWW':
                        alpha_var.append(i)
                        card=card.replace(i,"")
                        
            #---------------------Extracting name----------------- 
            Card_holder_Name=alpha_var[0] 
            
            #Extracting designation
            Designation=alpha_var[1]
            
            #Extracting company name
            if len(alpha_var)==3:
                Company_name=alpha_var[2]
            else:
                Company_name=alpha_var[2]+" "+alpha_var[3]
           
           #-----------------Extracting city,address,state from card variable---------------------------

            new_card=card.split()
            if new_card[4]=='St':
                 City=new_card[2]
            else:
                 City=new_card[3]
            if new_card[4]=="St":
                 State=new_card[3]
            else:
                 State=new_card[4]
            if new_card[4]=='St':
                 Address=new_card[0]+" "+new_card[4]+" "+new_card[1]
            else:
                 Address=new_card[0]+" "+new_card[1]+" "+new_card[2]


                    
            tab1,tab2,tab3=st.tabs([":blue[Extracted information using easyOCR]","Modified Information",":red[Upload to database]"],)
            with tab1:
                st.write(result)
            with tab2:
                st.write(':red[Name]        :', Card_holder_Name)
                st.write(':red[Company name]:', Company_name)
                st.write(':red[Designation] :', Designation)
                st.write(':red[Contact]     :', Phone)
                st.write(':red[Email id]    :', Email_id)
                st.write(':red[URL]         :', Web_Url)
                st.write(':red[Address]     :', Address)
                st.write(':red[City]        :', City)
                st.write(':red[State]       :', State)
                st.write(':red[Pincode]     :', Pincode)
            with tab3:
                st.write(":violet[If you wish to upload the business card data and an image to a database.Please click the below button.]")

                submit=st.button("Upload data")

                if submit:
                    with st.spinner("Please wait...."):
                        time.sleep(5)

                        sql = '''INSERT INTO card_info(Card_holder_Name,
                                                        Company_name,
                                                        Designation,
                                                        Contact_number,
                                                        Email,
                                                        Website_url,
                                                        Pincode,
                                                        Address,
                                                        City,
                                                        State,
                                                        image) 
                                                "VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                        
                        val = (Card_holder_Name,Company_name,Designation,Phone,Email_id,Web_Url,Pincode,Address,City,State,file_bytes)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        
                        st.success('Done,Uploaded to database successfully')


#---------------------------creating modify page-------------------------------
if selected=="Modify":
    #Creating dropdown menu
    selected1 = st.selectbox("Select a modification option",("Database","Image data","Update data","Delete data"))
    st.write(':red[You selected]:', selected1)
 #---------------------------------------to show database------------------------
    
    if selected1=="Database":
     # selecting all the data from database
        mycursor.execute("select * from card_info")
        mysql_data=mycursor.fetchall()
        df=pd.DataFrame(mysql_data,columns=mycursor.column_names)
        df.set_index("id",drop=True,inplace=True)
        st.table(df)
 #-----------------------------------------------to show image-------------------------#
     
    #-----------Extracting image based on name and designation-----------
        
    if selected1=='Image data':
        col1,col2=st.columns([3,3],gap='medium')
        with col1:

            mycursor.execute("SELECT card_holder_name,designation FROM card_info")
            rows = mycursor.fetchall()
            name = [row[0] for row in rows]   
            designation = [row[1] for row in rows]

        #------Fetching all the name and designation from database---------------
            selected_name = st.selectbox("SELECT NAME", name)     
            selected_designation = st.selectbox("SELECT DESIGNATION ", designation)

            if st.button('Display Image'):
                with col2:
                    sql = "SELECT image FROM card_info WHERE Card_holder_Name = %s AND Designation = %s "
                    mycursor.execute(sql,(selected_name,selected_designation))
                    result1 = mycursor.fetchone()

                    if result1 is not None:
                        image_data=result1[0]
                        nparr=np.frombuffer(image_data,np.uint8)
                        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        st.image(image, channels="BGR", width=400)
                    else:
                        st.error("Image not found for the given name and designation.Please choose the correct name and designation")

#-------------------------------------------update data--------------------------------------------
    if selected1=="Update data":
            #--------------Fetching all the name and designation from database-----------
            mycursor.execute("select card_holder_name,designation from card_info")
            rows=mycursor.fetchall()
            name = [row[0] for row in rows]   
            designation = [row[1] for row in rows]

            selected_name = st.selectbox("SELECT CARD HOLDER NAME TO UPDATE INTO THE DATABASE ", name)
            selected_designation = st.selectbox("SELECT DESIGNATION TO UPDATE INTO THE DATABASE ", designation)

            mycursor.execute("SHOW COLUMNS FROM card_info")
            columns = mycursor.fetchall()
            column_names = [i[0] for i in columns if i[0] not in ['id', 'image','card_holder_name','designation']]

            #----------Fetching all the column names-------------------- 
            select = st.selectbox("SELECT COLUMN TO UPDATE  ", column_names)
            new_data = st.text_input(f"Enter The New {select} To UPDATE")
            if st.button("Update"):
                # Defining  the  query to update the selected row
                sql = f"UPDATE card_info SET {select} = %s WHERE card_holder_name = %s AND designation = %s"
                #Executing  the query with the new data
                mycursor.execute(sql, (new_data, selected_name, selected_designation))
                # Commiting  the changes to the database
                mydb.commit()
                if mycursor.rowcount>0:
                  st.success("New data updated successfully!!")
                else:
                  st.error("Please choose the correct name and designation to update")
#---------------------------------delete data----------------------------------------------------------------

    if selected1=="Delete data":
        
        col1,col2=st.columns([2,3])
        
        with col1:
            mycursor.execute("select card_holder_name,designation from card_info")
            rows=mycursor.fetchall()
            name=[row[0] for row in rows]
            designation=[row[1] for row in rows]
            st.text("")
            selected_name=st.selectbox("SELECT CARD HOLDER NAME TO DELETE FROM DATABASE",name)
            selected_designation=st.selectbox("SELECT DESIGNATION TO DELETE FROM DATABASE",designation)
            if st.button("Delete"):
                sql="Delete from card_info WHERE Card_holder_Name = %s AND Designation = %s"
                mycursor.execute(sql,(selected_name,selected_designation))
                mydb.commit()
                if mycursor.rowcount>0:
                  st.success("Deleted Successfully!!")
                else:
                  st.error("Please select the correct name and designation to delete")

            with col2:
                st.write(":green[The changes made to the database are shown in the table.]")
                mycursor.execute('select * from card_info')
                updated_data=mycursor.fetchall()
                df=pd.DataFrame(updated_data,columns=mycursor.column_names)
                df.set_index("id",drop=True,inplace=True)
                st.dataframe(df)

#------------------------------------------------FINISH--------------------------------------------------------------------------   