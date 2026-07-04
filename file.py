from datetime import datetime

class BaseReportGenerator:
    def __init__(self, db_session):
        self.db = db_session                 
        self.status = "initialized"          
        self._report_date = datetime.now()   
    def generate(self, org_id: int) -> dict:  
        self._prepare_data(org_id)
        return self._format_output()

    def _prepare_data(self, org_id: int):     
        pass 

    def _format_output(self) -> dict:         
        return {"date": self._report_date, "status": self.status}


class ShelterReportGenerator(BaseReportGenerator):
    def __init__(self, db_session):
        super().__init__(db_session)          
        self._animal_count = 0                

    def _prepare_data(self, org_id: int):     
        self._animal_count = 15               
        self.status = "data_loaded"

    def get_summary(self) -> str:             
        return f"Shelter has {self._animal_count} animals."


class HotelInvoiceGenerator(BaseReportGenerator):
    def __init__(self, db_session):
        super().__init__(db_session)          
        self._total_revenue = 0.0             
        self.currency = "UAH"                 

    def _prepare_data(self, org_id: int):     
        self._total_revenue = 5000.0          
        self.status = "calculated"

    def apply_discount(self, percent: float): 
        self._total_revenue *= (1 - percent/100)


class ReportController:
    def __init__(self):
        self.generator_type = "default"       

    def create_shelter_report(self, session, org_id: int):
        gen = ShelterReportGenerator(session) 
        return gen.generate(org_id)

    def create_hotel_invoice(self, session, org_id: int):
        gen = HotelInvoiceGenerator(session)  
        gen.apply_discount(10)
        return gen.generate(org_id)