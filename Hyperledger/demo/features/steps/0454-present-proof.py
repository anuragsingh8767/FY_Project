from bdd_support.agent_backchannel_client import (
    agent_container_POST,
    aries_container_request_proof,
    aries_container_verify_proof,
    async_sleep,
    read_proof_req_data,
)
from behave import then, when

# This step is defined in another feature file
# Given "Acme" and "Bob" have an existing connection
# And "Bob" has an issued <Schema_name> credential <Credential_data> from <issuer>


@when(
    '"{verifier}" sends a request for proof presentation {request_for_proof} to "{prover}"'
)
def step_impl(context, verifier, request_for_proof, prover):
    agent = context.active_agents[verifier]

    proof_request_info = read_proof_req_data(request_for_proof)

    # replace any restrictions that need the cred def id...
    cred_def_id = context.cred_def_id
    cred_def_restrictions = [{"cred_def_id": cred_def_id}]

    if "cred_def_restriction" in proof_request_info["requested_attributes"]:
        proof_request_info["requested_attributes"]["cred_def_restriction"][
            "restrictions"
        ] = cred_def_restrictions

    if "cred_def_predicate" in proof_request_info["requested_predicates"]:
        proof_request_info["requested_predicates"]["cred_def_predicate"][
            "restrictions"
        ] = cred_def_restrictions

    proof_exchange = aries_container_request_proof(
        agent["agent"],
        proof_request_info,
        is_anoncreds=agent["agent"].wallet_type == "askar-anoncreds",
    )

    context.proof_request = proof_request_info
    context.proof_exchange = proof_exchange


@when(
    '"{verifier}" sends a request with explicit revocation status for proof presentation {request_for_proof} to "{prover}"'
)
def step_impl(context, verifier, request_for_proof, prover):
    agent = context.active_agents[verifier]

    proof_request_info = read_proof_req_data(request_for_proof)

    proof_exchange = aries_container_request_proof(
        agent["agent"],
        proof_request_info,
        explicit_revoc_required=True,
        is_anoncreds=agent["agent"].wallet_type == "askar-anoncreds",
    )

    context.proof_request = proof_request_info
    context.proof_exchange = proof_exchange


@then('"{verifier}" has the proof verified')
def step_impl(context, verifier):
    agent = context.active_agents[verifier]

    proof_request = context.proof_request

    # check the received credential status (up to 10 seconds)
    for i in range(10):
        async_sleep(1.0)
        verified = aries_container_verify_proof(agent["agent"], proof_request)
        if verified is not None and verified.lower() == "true":
            return

    assert False


@then('"{verifier}" has the proof verification fail')
def step_impl(context, verifier):
    agent = context.active_agents[verifier]

    proof_request = context.proof_request

    # check the received credential status (up to 10 seconds)
    for i in range(10):
        async_sleep(1.0)
        verified = aries_container_verify_proof(agent["agent"], proof_request)
        if verified is not None and verified.lower() == "false":
            return

    assert False


@when(
    '"{verifier}" sends a request for json-ld proof presentation {request_for_proof} to "{prover}" with {sig_type}'
)
def step_impl(context, verifier, request_for_proof, prover, sig_type):
    agent = context.active_agents[verifier]
    prover_agent = context.active_agents[prover]

    proof_request_info = {
        "comment": "test proof request for json-ld",
        "connection_id": agent["agent"].agent.connection_id,
        "presentation_request": {
            "dif": {
                "options": {
                    "challenge": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                    "domain": "4jt78h47fh47",
                },
                "presentation_definition": {
                    "id": "32f54163-7166-48f1-93d8-ff217bdb0654",
                    "format": {"ldp_vp": {"proof_type": [sig_type]}},
                    "input_descriptors": [
                        {
                            "id": "citizenship_input_1",
                            "name": "EU Driver's License",
                            "schema": [
                                {
                                    "uri": "https://www.w3.org/2018/credentials#VerifiableCredential"
                                },
                                {"uri": "https://w3id.org/citizenship#PermanentResident"},
                            ],
                            "constraints": {
                                "limit_disclosure": "required",
                                "is_holder": [
                                    {
                                        "directive": "required",
                                        "field_id": [
                                            "1f44d55f-f161-4938-a659-f8026467f126"
                                        ],
                                    }
                                ],
                                "fields": [
                                    {
                                        "id": "1f44d55f-f161-4938-a659-f8026467f126",
                                        "path": ["$.credentialSubject.familyName"],
                                        "purpose": "The claim must be from one of the specified person",
                                        "filter": {"const": "SMITH"},
                                    },
                                    {
                                        "path": ["$.credentialSubject.givenName"],
                                        "purpose": "The claim must be from one of the specified person",
                                    },
                                ],
                            },
                        }
                    ],
                },
            }
        },
    }

    proof_exchange = agent_container_POST(
        agent["agent"],
        "/present-proof-2.0/send-request",
        proof_request_info,
    )

    context.proof_request = proof_request_info
    context.proof_exchange = proof_exchange


@then('"{verifier}" has the json-ld proof verified')
def step_impl(context, verifier):
    agent = context.active_agents[verifier]

    pass
