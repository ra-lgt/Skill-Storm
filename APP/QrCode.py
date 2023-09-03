import base64
from io import BytesIO
import qrcode


class Qr_Code:

	def generate_qr_code(self,data):
		data="upi://pay?pa=raviajay9344@okhdfcbank&pn=Skill-Storm&am={}&tn={}&cu=INR".format(data['ind_price'],data['title'][0]) 
		qr = qrcode.make(data)


		buffer = BytesIO()
		qr.save(buffer, format="PNG")
		qr_bytes = buffer.getvalue()
		qr_base64 = base64.b64encode(qr_bytes).decode("utf-8")

		return qr_base64
		





