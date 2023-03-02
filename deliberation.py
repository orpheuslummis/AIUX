# TODO text doesn't disappear upon change

from dataclasses import dataclass
import openai
import streamlit as st

from utils import RequestParams, new_logger, get_params_from_env, request

log = new_logger("deliberation")

TEMPERATURE = 0.6
MAX_TOKENS = 300
N = 4


@dataclass
class Params:
    prompt: str


class Pipeline:
    name: str

    def run(self, _: Params):
        pass


class Dummy(Pipeline):
    name = "dummy"


class Critic(Pipeline):
    """
    Pipeline that critics a prompt in various ways (expansion), then aggregates them into a short summary.
    """

    name = "critic"
    default_n = 5
    default_max_tokens = 300
    default_temperature = 0.777

    critics = {
        "critic1": """
        Provide criticism for the following idea:

        {idea}
        """,
        "critic2": """
        List points of potential lack of clarity, robustness, coherence, etc. in the following idea:
        
        {idea}
        """,
    }

    @staticmethod
    def aggregate_results(results) -> str:
        sep = "–––"
        joined_results = sep.join(results)

        aggregation_prompt = """
        The following are the results of the critics:

        {results}

        Represent clearly the given criticism as bullet points.
        """

        p = aggregation_prompt.format(results=joined_results)
        r = request(
            RequestParams(
                prompt=p,
                n=1,
                max_tokens=500,
                temperature=0.5,
            )
        )
        print(f"DEBUG: {r}")
        return r

    def run(self, params: Params) -> str:
        results_from_critics = []

        for critic in self.critics:
            prompt = critic.format(idea=params.prompt)

            r = request(
                RequestParams(
                    prompt=prompt,
                    n=self.default_n,
                    max_tokens=self.default_max_tokens,
                    temperature=self.default_temperature,
                )
            )
            for i, rr in enumerate(r):
                log.debug(f"{critic} result {i}: {rr}")
            results_from_critics.extend(r)

        aggregated_results = self.aggregate_results(results_from_critics)
        log.info(f"aggregated_results: {aggregated_results}")
        return aggregated_results


class PraisePipeline(Pipeline):
    """
    Pipeline that comes up with various aspects to praise of a prompt, (expansion),
    then aggregates them into a short summary.
    """

    name = "praise"
    default_n = 5
    default_max_tokens = 100
    default_temperature = 0.9

    praises = {
        "simple": """
        Provide praise for the following:

        {data}
        """,
        "list": """
        List aspects of this to be praised:

        {data}
        """,
    }

    def run(self, params: Params):
        results = {}
        for k in self.praises:
            prompt = self.praises[k].format(data=params.prompt)

            r = request(
                RequestParams(
                    prompt=prompt,
                    n=self.default_n,
                    max_tokens=self.default_max_tokens,
                    temperature=self.default_temperature,
                )
            )
            for i, r in enumerate(results):
                log.debug(f"result {i}: ???")

            results[k] = r

        aggregated_results = self.aggregate_results(results)
        log.info(f"aggregated_results: {aggregated_results}")
        return aggregated_results

    @staticmethod
    def aggregate_results(rd: dict[str, str]) -> str:
        # preprocess results
        # extract them from the dict and join them

        rvalues = [rd[r] for r in rd]

        sep = "–––\n"
        joined_results = sep.join(rvalues)

        aggregation_prompt = """
        The following are the many praises:

        {results}

        Represent clearly the given praises as bullet points.
        """

        p = aggregation_prompt.format(results=joined_results)
        result = request(
            RequestParams(
                prompt=p,
                n=1,
                max_tokens=500,
                temperature=0.5,
            )
        )
        # TODO extract text from response
        print(f"DEBUG: {result}")
        return result


class Improver(Pipeline):
    """
    Identify useful improvements, then rewrite the initial prompt,
    integrating the suggested improvements.
    """

    pass


def run_pipeline_set(pipelines: list[Pipeline], params: Params) -> dict:
    # TBD async
    # TBD configurable set of pipelines to run
    results = {}
    for p in pipelines:
        results[p.name] = p.run(params)
    return results


def update_prompt():
    params = Params(
        prompt=st.session_state.prompt,
    )
    results = run_pipeline_set(pipelines, params)

    for pname in results:
        st.header(pname)
        st.markdown(results[pname].text)


if __name__ == "__main__":
    params = get_params_from_env()
    if params["apikey"] is None:
        st.error("Please set OPENAI_API_KEY environment variable.")
    openai.api_key = params["apikey"]

    pipelines: list[Pipeline] = [Dummy(), Critic(), PraisePipeline()]

    container_top = st.container()
    container_bottom = st.container()

    with container_top:
        st.header("Deliberation system")
        st.text_area("Prompt", key="prompt")
        if st.button("Submit"):
            update_prompt()

        with st.expander("Advanced"):
            st.write("TBD advanced parameters")
