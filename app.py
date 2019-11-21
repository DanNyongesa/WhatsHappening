from scrapper.ticket_sasa import ScrapTicketSasa
from scrapper.machinery import run_action_class

scrap_ticket_sasa_action = ScrapTicketSasa(payload={})
result = run_action_class(scrap_ticket_sasa_action)
print(result.response)


