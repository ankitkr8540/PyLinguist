import argparse
from pathlib import Path
import sys
from data.input.preprocessor import DatasetPreprocessor 
from pylinguist.utils.partial_translator import partial_translate_examples
from pylinguist.utils.logger import setup_logger

# Setup logger
logger = setup_logger()


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='PyLinguist - Code Translation Pipeline')
    
    # Data preprocessing arguments
    parser.add_argument('--preprocess-only', action='store_true',
                      help='Only run preprocessing without translation')
    parser.add_argument('--dataset', type=str,
                      default="jtatman/python-code-dataset-500k",
                      help='HuggingFace dataset name for preprocessing')
    parser.add_argument('--batch-size', type=int, default=1000,
                      help='Batch size for preprocessing')
    parser.add_argument('--force-preprocess', action='store_true',
                      help='Force preprocessing even if dataset exists')
    
    # number of samples to be translated split into train, test
    parser.add_argument('--start-index', type=int, default=0,
                      help='Start index for translation')
    parser.add_argument('--test-samples', type=int, default=10,
                      help='Number of test samples to translate')
    parser.add_argument('--train-samples', type=int, default=30,
                      help='Number of training samples to translate')
    
    # Partial translation arguments
    parser.add_argument('--source-lang', type=str,
                      help='Source language code (e.g., en)')
    parser.add_argument('--target-lang', type=str,
                        help='Target language code (e.g., hi)')
    parser.add_argument('--stage1', type=str, choices=['google', 'deepl'],
                        help='Stage 1 translation service')
    parser.add_argument('--stage2', type=str,
                        choices=['gpt', 'llama', 'claude'],
                        help='Stage 2 translation model (optional)')
        
    return parser.parse_args()

def check_dataset_exists():
    """Check if preprocessed dataset exists."""
    dataset_path = Path("data/input/samples/python_code_dataset.csv")
    stats_path = Path("data/input/samples/dataset_stats.json")
    return dataset_path.exists() and stats_path.exists()

def check_partial_translation_exists(args):
    """Check if partial translation results exist."""
    print(args)
    output_dir = Path("data/output/partial_translation")
    return any(output_dir.glob(f"partial_translation_{args.source_lang}_{args.target_lang}_{args.start_index}_{args.train_samples}_{args.test_samples}.csv"))

def run_preprocessing(args):
    """Run the preprocessing pipeline."""
    try:
        logger.info("Starting preprocessing pipeline...")
        preprocessor = DatasetPreprocessor("data/input/samples")
        
        results = preprocessor.process_and_save_dataset(args)
        
        if results['success']:
            logger.info("Preprocessing completed successfully!")
            logger.info(f"Dataset saved to: {results['output_path']}")
            logger.info("\nDataset Statistics:")
            for key, value in results['stats'].items():
                logger.info(f"{key}: {value}")
            return True
        else:
            logger.error(f"Preprocessing failed: {results.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"Error during preprocessing: {str(e)}")
        return False

def run_partial_translation(args):
    """Run partial translation using Joshua keywords."""
    try:
       
        
        logger.info("Starting partial translation using Joshua keywords...")
        
        dataset_path = Path("data/input/samples/python_code_dataset.csv")
        
        # Run partial translation
        results = partial_translate_examples(
            data_path=dataset_path,
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            start_index=args.start_index,
            test_samples=args.test_samples,
            train_samples=args.train_samples
        )
        
        # Save results
        output_dir = Path("data/output/partial_translation")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        output_file = output_dir / f"partial_translation_{args.source_lang}_{args.target_lang}_{args.start_index}_{args.train_samples}_{args.test_samples}.csv"
        
        results.to_csv(output_file, index=False)
            
        logger.info(f"Partial translation completed. Results saved to: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Error during partial translation: {str(e)}")
        return False
    
def run_translation(args):
    """Run the translation pipeline."""
    # Import here to avoid circular imports
    from pylinguist.models.pipeline import TranslationPipeline
    
    try:
        pipeline = TranslationPipeline(
            source_lang=args.source_lang,
            target_lang=args.target_lang,
            stage1_model=args.stage1,
            stage2_model=args.stage2
        )
        
        return pipeline.run()
        
    except Exception as e:
        logger.error(f"Error during translation: {str(e)}")
        return False

def main():
    args = parse_args()

    #----------------------------------------- preprocessing and Data loading begins -----------------------------------------
    # Check if preprocessing is needed
    dataset_exists = check_dataset_exists()
    partial_translation_exists = check_partial_translation_exists(args)
    need_preprocessing = args.force_preprocess or not dataset_exists

    
    if need_preprocessing:
        logger.info("Dataset not found or force preprocessing enabled.")
        if not run_preprocessing(args):
            sys.exit(1)
    else:
        logger.info("Dataset found. Skipping preprocessing.")
    
    # If only preprocessing was requested, exit here
    if args.preprocess_only:
        logger.info("Preprocessing completed. Exiting as requested.")
        sys.exit(0)
    #----------------------------------------- preprocessing ends --------------------------------------------

    # Validate translation arguments
    if not all([args.source_lang, args.target_lang]):
        logger.error("Missing required translation arguments.")
        logger.error("Please provide --source-lang, --target-lang, and --stage1")
        sys.exit(1)
    elif args.stage1 and not args.stage2:
        logger.info(f"Starting translation pipeline... with stage 1 {args.stage1} only (no stage 2)")
    elif args.stage1 and args.stage2:
        logger.info(f"Starting translation pipeline... with stage 1 {args.stage1} and stage 2 {args.stage2}")

    #--------------------- partial translation begins based on joshua keywords--------------------------------

    if not partial_translation_exists:
        if not run_partial_translation(args):
            sys.exit(1)
    else:
        logger.info("Partial translation results found. Skipping partial translation.")
    #--------------------- partial translation ends --------------------------------

    
    # # Run translation
    # if not run_translation(args):
    #     sys.exit(1)
    
    logger.info("Pipeline completed successfully!")

if __name__ == "__main__":
    main()