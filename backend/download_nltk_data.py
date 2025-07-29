import nltk
import ssl

def download_nltk_resources():
    """
    Downloads all necessary NLTK resources for the application.
    This includes 'punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', and the specific 'punkt_tab'.
    It handles SSL context for environments where it's needed.
    """
    # Added 'punkt_tab' to the list of resources
    resources = ['punkt', 'stopwords', 'wordnet', 'averaged_perceptron_tagger', 'punkt_tab']
    
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    print("--- Starting NLTK Resource Download ---")
    for resource in resources:
        try:
            print(f"Downloading NLTK resource: '{resource}'...")
            # NLTK's download function is idempotent. It won't re-download if the resource is up-to-date.
            nltk.download(resource)
            print(f"Resource '{resource}' is available.")
        except Exception as e:
            print(f"Could not download resource '{resource}'. Error: {e}")
            if resource == 'punkt_tab':
                print("Note: 'punkt_tab' might be an unofficial or special-purpose resource.")
    print("--- NLTK Resource Download Finished ---")


if __name__ == "__main__":
    download_nltk_resources()

